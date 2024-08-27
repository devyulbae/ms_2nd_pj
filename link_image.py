# link_image.py
import pandas as pd
import os

image_dir = 'images'
csv_dir = 'jeju_list_0822.csv'

def link_image(name):
    df = pd.read_csv(csv_dir, encoding='utf-8')
    matching_row = df[df['name'] == name]
    
    if not matching_row.empty:
        picture_filename = matching_row.iloc[0]['picture']
        image_path = os.path.join(image_dir, f'{picture_filename}.jpg')
        
        if os.path.exists(image_path):
            # '/static/' 경로를 반환하여 Django가 이미지 파일을 서빙할 수 있도록 설정
            return f'/static/{picture_filename}.jpg'
        else:
            print(f"Error: 이미지 파일 {image_path}을(를) 찾을 수 없습니다.")
            return '/static/image_not_found.jpg'
    
    return '/static/image_not_found.jpg'
