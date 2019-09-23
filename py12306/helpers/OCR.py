import math
import random
from py12306.config import Config
from py12306.verify.localVerifyCode import verify
from py12306.helpers.api import API_FREE_CODE_QCR_API
from py12306.helpers.request import Request
from py12306.log.common_log import CommonLog
from py12306.vender.ruokuai.main import RKClient


class OCR:
    """
    图片识别
    """
    session = None

    def __init__(self):
        self.session = Request()

    @classmethod
    def get_img_position(cls, img):
        """
        获取图像坐标
        :param img_path:
        :return:
        """
        self = cls()
        if Config().AUTO_CODE_PLATFORM == 'free_1':
            return self.get_image_by_free_site(img)
        elif Config().AUTO_CODE_PLATFORM == 'free_2':
            return self.get_image_by_local_verify(img)
        return self.get_img_position_by_ruokuai(img)

    def get_img_position_by_ruokuai(self, img):
        ruokuai_account = Config().AUTO_CODE_ACCOUNT
        soft_id = '119671'
        soft_key = '6839cbaca1f942f58d2760baba5ed987'
        rc = RKClient(ruokuai_account.get('user'), ruokuai_account.get('pwd'), soft_id, soft_key)
        result = rc.rk_create(img, 6113)
        if "Result" in result:
            return self.get_image_position_by_offset(list(result['Result']))
        CommonLog.print_auto_code_fail(result.get("Error", CommonLog.MESSAGE_RESPONSE_EMPTY_ERROR))
        return None

    def get_image_position_by_offset(self, offsets):
        positions = []
        width = 75
        height = 75
        for offset in offsets:
            random_x = random.randint(-5, 5)
            random_y = random.randint(-5, 5)
            offset = int(offset)
            x = width * ((offset - 1) % 4 + 1) - width / 2 + random_x
            y = height * math.ceil(offset / 4) - height / 2 + random_y
            positions.append(int(x))
            positions.append(int(y))
        return positions

    def get_image_by_free_site(self, img):
        data = {
            'img': img
        }
        response = self.session.post(API_FREE_CODE_QCR_API, data=data)
        result = response.json()
        if result.get('msg') == 'success':
            pos = result.get('result')
            return self.get_image_position_by_offset(pos)

        CommonLog.print_auto_code_fail(CommonLog.MESSAGE_GET_RESPONSE_FROM_FREE_AUTO_CODE)
        return None

    def get_image_by_local_verify(self, img):
        with open('./tkcode.png', 'rb') as f:
            result = f.read()
        result = verify(result)
        print(result)
        return self.codexy(Ofset=result, is_raw_input=False)

    def codexy(self, Ofset=None, is_raw_input=True):
        """
        获取验证码
        :return: str
        """
        if is_raw_input:
            print(u"""
                *****************
                | 1 | 2 | 3 | 4 |
                *****************
                | 5 | 6 | 7 | 8 |
                *****************
                """)
            print(u"验证码分为8个，对应上面数字，例如第一和第二张，输入1, 2  如果开启cdn查询的话，会冲掉提示，直接鼠标点击命令行获取焦点，输入即可，不要输入空格")
            print(u"如果是linux无图形界面，请使用自动打码，is_auto_code: True")
            print(u"如果没有弹出验证码，请手动双击根目录下的tkcode.png文件")
            Ofset = input(u"输入对应的验证码: ")
        if isinstance(Ofset, list):
            select = Ofset
        else:
            Ofset = Ofset.replace("，", ",")
            select = Ofset.split(',')
        post = []
        offsetsX = 0  # 选择的答案的left值,通过浏览器点击8个小图的中点得到的,这样基本没问题
        offsetsY = 0  # 选择的答案的top值
        for ofset in select:
            if ofset == '1':
                offsetsY = 77
                offsetsX = 40
            elif ofset == '2':
                offsetsY = 77
                offsetsX = 112
            elif ofset == '3':
                offsetsY = 77
                offsetsX = 184
            elif ofset == '4':
                offsetsY = 77
                offsetsX = 256
            elif ofset == '5':
                offsetsY = 149
                offsetsX = 40
            elif ofset == '6':
                offsetsY = 149
                offsetsX = 112
            elif ofset == '7':
                offsetsY = 149
                offsetsX = 184
            elif ofset == '8':
                offsetsY = 149
                offsetsX = 256
            else:
                pass
            post.append(offsetsX)
            post.append(offsetsY)
        # randCode = str(post).replace(']', '').replace('[', '').replace("'", '').replace(' ', '')
        print(u"验证码识别坐标为{0}".format(post))
        # return randCode
        return post

if __name__ == '__main__':
    pass
    # code_result = AuthCode.get_auth_code()
