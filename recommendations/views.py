# recommendations/views.py
# recommendations/views.py
import sys
import os
import json
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from link_image import link_image

def jeju_intro(request):
    categories = ["맛집", "카페", "해변", "관광지", "포토스팟"]
    return render(request, 'recommendations/jeju_intro.html', {'categories': categories})

def set_jeju_region(request, region):
    if region in ['east', 'west']:
        request.session['jeju_region'] = '동제주' if region == 'east' else '서제주'
    return redirect('index')

RECOMMENDATION_HISTORY_KEY = 'recommendation_history'
def recommend(request, category):
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    jeju_region = request.session.get('jeju_region', '전체')

    recommendation_history = request.session.get(RECOMMENDATION_HISTORY_KEY, {})
    if category not in recommendation_history:
        recommendation_history[category] = []

    recommendations = get_recommendations(category, latitude, longitude, recommendation_history[category], jeju_region)
    
    recommendation_history[category].append(recommendations['name'])
    request.session[RECOMMENDATION_HISTORY_KEY] = recommendation_history

    image_path = link_image(recommendations['name'])

    context = {
        'category': category,
        'recommendations': recommendations,
        'image_path': image_path,
        'jeju_region': jeju_region
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('recommendations/recommend_content.html', context)
        return JsonResponse({'html': html})

    # 일반 요청일 경우 전체 페이지 렌더링
    return render(request, 'recommendations/recommend.html', context)

def index(request):
    return render(request, 'recommendations/index.html')

def get_recommendations(category, latitude, longitude, previous_recommendations, jeju_region):
    sys.stdout.reconfigure(encoding='utf-8')
    
    exclude_condition = ""
    if previous_recommendations:
        exclude_condition = f" {', '.join(previous_recommendations)} 이름을 가진 장소들은 제외해줘."
    print(jeju_region)

    region_condition = f" {jeju_region}에 있는" if jeju_region != '전체' else "제주도에"

    input_string = f"현재 나의 위치는 위도 {latitude}, 경도 {longitude}이다. {region_condition}  {category} 장소를 1개 알려줘. name은 장소이름이다. user_review는 사용자 리뷰를 보고 써달라. duration_time은 현재 나의 위치에서 자동차로 걸리는 시간이다.{exclude_condition}"

    # Azure OpenAI 설정
    endpoint = os.getenv("ENDPOINT_URL", "https://ojo-ai-services2.openai.azure.com/")
    deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
    search_endpoint = os.getenv("SEARCH_ENDPOINT", "https://ojo-ai-search.search.windows.net")
    search_key = os.getenv("SEARCH_KEY", "LAQvu2gep6KC8cgg7XfubtflXmPXmkV2BdERHjGx4mAzSeBkrPgB")
    search_index = os.getenv("SEARCH_INDEX_NAME", "jeju")

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default")

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        azure_ad_token_provider=token_provider,
        api_version="2024-05-01-preview",
    )

    completion = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "user",
                "content": input_string  # Using the input string here
            }
        ],
        max_tokens=1200,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False,
        extra_body={
            "data_sources": [{
                "type": "azure_search",
                "parameters": {
                    "endpoint": f"{search_endpoint}",
                    "index_name": "jeju",
                    "semantic_configuration": "jeju",
                    "query_type": "semantic",
                    "fields_mapping": {},
                    "in_scope": False,
                    "role_information": r"너는 제주도 여행 전문가이다. 출력은 API로 해주고 출력형태는 Json 데이터 형태는 {name: location: user_review: duration_time: }, 출력을 제외하고 어떤 미사어구도 붙이지마라.",
                    "filter": None,
                    "strictness": 3,
                    "top_n_documents": 5,
                    "authentication": {
                        "type": "api_key",
                        "key": f"{search_key}"
                    }
                }
            }]
        }
    )

    completion_dict = json.loads(completion.to_json())
    content = completion_dict['choices'][0]['message']['content']
    print(content)
    content = content.replace("json", "").replace("`", "").strip()
    data = json.loads(content)
    print(data)
    # 반환된 데이터가 단일 객체이므로 리스트가 아닌 단일 객체로 반환
    return data