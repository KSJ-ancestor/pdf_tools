from PIL import Image
import os

def convert_png_to_ico(png_path, ico_path, sizes=[(8,8), (16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]):
    # PNG 파일 열기
    img = Image.open(png_path)

    # ICO 파일로 저장
    img.save(ico_path, format='ICO', sizes=sizes)

if __name__ == "__main__":
    # 변환할 PNG 파일 경로 입력
    png_file = "cowpower.png" #input("PNG 파일 경로를 입력하세요: ")

    # 저장할 ICO 파일 경로 입력
    ico_file = "cowpower.ico" #input("ICO 파일 경로를 입력하세요: ")

    # PNG 파일을 ICO 파일로 변환
    if os.path.exists(png_file):
        convert_png_to_ico(png_file, ico_file)
        print(f"{png_file} -> {ico_file} 변환 완료")
    else:
        print(f"파일 {png_file}이(가) 존재하지 않습니다.")
