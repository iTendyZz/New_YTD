import rutube
from telegram import InlineKeyboardButton

class VLoader:
    def __init__(self, url):
        self.object = rutube.Rutube(url)
    

    def check_video_info(self):
        '''Возвращает данные о видео:
1) Ссылка на пикчу
2) Название
3) Описание (первые сто символов)
4) Длительность
5) Для взрослых (опционально)
6) Inline кнопки с доступными разрешениями'''
        data = self.object._get_data()
        pic = data["thumbnail_url"]
        title = data["title"]
        desc = data["description"]
        duration = data["duration"]
        is18plus = data["is_adult"]
        res_list = self.object.available_resolutions
        res_buttons = []
        for res in res_list:
            button = [InlineKeyboardButton(text=(str(res) + "p"), callback_data=f"get_res_{res}")]
            res_buttons.append(button)
        return [pic, title, desc[0:100:], duration, is18plus, res_buttons]
    

    def download(self, resolution, filename):
        filepath = f"downloads/rutube/"
        with open(f"{filepath}{filename}.mp4", "wb") as f:
            self.object.get_by_resolution(int(resolution)).download(stream=f)
        return f'{filepath}{filename}.mp4'
    
