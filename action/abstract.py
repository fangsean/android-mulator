import asyncio
import json
import logging
import os.path
from abc import ABC
from typing import *

import numpy as np
import pandas as pd
from airtest.core.api import *

import util.multiprocessing as func
from action.databases import user_all, user_query, user_quantity_step, user_quantity_stage, user_delete
from click_positioning import CONTINUOUS_BATTLE_BUTTON_MY_X, CONTINUOUS_BATTLE_BUTTON_MY_Y, \
    CONTINUOUS_BATTLE_BUTTON_LOGIN_X, \
    CONTINUOUS_BATTLE_BUTTON_LOGIN_Y, CONTINUOUS_BATTLE_BUTTON_INPUT_USERNAME_Y, \
    CONTINUOUS_BATTLE_BUTTON_INPUT_USERNAME_X, CONTINUOUS_BATTLE_BUTTON_INPUT_PASSWORD_X, \
    CONTINUOUS_BATTLE_BUTTON_INPUT_PASSWORD_Y, CONTINUOUS_BATTLE_BUTTON_INPUT_SUBMIT_Y, \
    CONTINUOUS_BATTLE_BUTTON_INPUT_SUBMIT_X, CONTINUOUS_BATTLE_SWIPE_START_X, CONTINUOUS_BATTLE_SWIPE_START_Y, \
    CONTINUOUS_BATTLE_BUTTON_INPUT_MANAGER_X, \
    CONTINUOUS_BATTLE_BUTTON_INPUT_MANAGER_Y, CONTINUOUS_BATTLE_BUTTON_INPUT_KAOHE_Y, \
    CONTINUOUS_BATTLE_BUTTON_INPUT_KAOHE_X, CONTINUOUS_BATTLE_BUTTON_LOGOUT_Y, CONTINUOUS_BATTLE_BUTTON_LOGOUT_X, \
    CONTINUOUS_BATTLE_BUTTON_INPUT_USERNAME_CLEAR_Y, CONTINUOUS_BATTLE_BUTTON_INPUT_USERNAME_CLEAR_X, \
    CONTINUOUS_BATTLE_BUTTON_INPUT_PASSWORD_CLEAR_Y, CONTINUOUS_BATTLE_BUTTON_INPUT_PASSWORD_CLEAR_X, \
    CONTINUOUS_BATTLE_BUTTON_INPUT_XINBANBIXUE_X, CONTINUOUS_BATTLE_BUTTON_INPUT_XINBANBIXUE_Y, \
    CONTINUOUS_BATTLE_BUTTON_LIEBIAO_Y, CONTINUOUS_BATTLE_BUTTON_LIEBIAO_X, CONTINUOUS_BATTLE_SWIPE_LIEBIAO_START_X, \
    CONTINUOUS_BATTLE_SWIPE_LIEBIAO_START_Y, CONTINUOUS_BATTLE_SWIPE_LIEBIAO_END_X, \
    CONTINUOUS_BATTLE_SWIPE_LIEBIAO_END_Y, CONTINUOUS_BATTLE_BUTTON_BACK_Y, CONTINUOUS_BATTLE_BUTTON_BACK_X, \
    CONTINUOUS_BATTLE_BUTTON_AGREE_X, CONTINUOUS_BATTLE_BUTTON_AGREE_Y, CONTINUOUS_SCREENCAP_START_X, \
    CONTINUOUS_SCREENCAP_START_Y, CONTINUOUS_SCREENCAP_END_Y, CONTINUOUS_SCREENCAP_END_X, \
    CONTINUOUS_BATTLE_BUTTON_INPUT_SAVE_X, CONTINUOUS_BATTLE_BUTTON_INPUT_SAVE_Y, \
    CONTINUOUS_BATTLE_BUTTON_AGREE_CAT_START_X, CONTINUOUS_BATTLE_BUTTON_AGREE_CAT_END_X, \
    CONTINUOUS_BATTLE_BUTTON_AGREE_CAT_START_Y, CONTINUOUS_BATTLE_BUTTON_AGREE_CAT_END_Y
from config import *
from util import LazyValue
from util.adb_utils import AdbUtils
from util.image_utils import ImageUtils
from util.key_code import *
from util.thread_pool import loop_executor

logger = logging.getLogger('bgo_script.attacher')


class AbstractAction:
    """
    AbstractAction defines the basic interface to interact with the game application
    """

    def get_ports(self) -> np.ndarray:
        return np.arange(self.first, self.first + self.num * 32, 32, dtype=np.int32)

    @staticmethod
    async def init(device_id, *args, **kwargs):
        try:
            adb = AdbUtils(device_id)
            adb.connect()
            if not adb.isInstall(package_name):
                print('未安装{},'.format(package_name))
                adb.installApp(apk_file)
                retry = 3
                while not adb.isInstall(package_name) and retry > 0:
                    print('retry {} {},'.format(device_id, retry))
                    retry -= 1
                    await asyncio.sleep(2)
            # adb.sendKeyEvent(POWER)
            # adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_AGREE_X, CONTINUOUS_BATTLE_BUTTON_AGREE_Y)
            # stop_app(package_name)
            logger.info('subprocesses done for init for %s' % device_id)
        except Exception as ex:
            logger.error('subprocesses done for init for %s' % device_id)
            logger.error(str(ex))

    @staticmethod
    def run(args):
        host = args['host']
        port = args['port']
        machine = host + "_" + port
        device_id = args['device_id']
        username = args['username']
        password = args['password']
        # username
        user = user_query(username)
        if not user:
            return
        adb = AdbUtils(device_id)
        try:
            adb.connect()
            if not adb.isInstall(package_name):
                print('{}未安装{},无法执行'.format(device_id, package_name))
                raise Exception('{}未安装{},无法执行'.format(device_id, package_name))
            logger.info('subprocesses done at watch video for %s in %s' % (username, device_id))
            sleep(3)
            component = "/".join([package_name, activity])
            adb.sendKeyEvent(POWER)
            adb.startActivity(component)
            sleep(3)
            for i in range(0, 5):
                adb.sendKeyEvent(BACK)
            adb.startActivity(component)
            sleep(3)
            image_utils = ImageUtils(device_id)
            image_name = image_utils.screenShot()
            image_utils.writeToFile(os.path.join(base_photops, machine), image_name)
            sleep(1)
            image = image_utils.loadImage(os.path.join(base_photops, machine, image_name))
            sleep(1)
            logger.info('image width %s height %s' % (image.size[0], image.size[1]))
            words = image_utils.has_words(os.path.join(base_photops, machine, image_name),
                                                 CONTINUOUS_BATTLE_BUTTON_AGREE_CAT_START_X,
                                                 CONTINUOUS_BATTLE_BUTTON_AGREE_CAT_END_X,
                                                 CONTINUOUS_BATTLE_BUTTON_AGREE_CAT_START_Y,
                                                 CONTINUOUS_BATTLE_BUTTON_AGREE_CAT_END_Y)
            if "暂不同意" in words:
                adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_AGREE_X, CONTINUOUS_BATTLE_BUTTON_AGREE_Y)
            elif "取消" in words:
                # 保存
                adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_INPUT_SAVE_X, CONTINUOUS_BATTLE_BUTTON_INPUT_SAVE_Y)
                sleep(1)
                # 我的
                logger.info('subprocesses done at 我的 for %s in %s' % (username, device_id))
                adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_MY_X, CONTINUOUS_BATTLE_BUTTON_MY_Y)
                sleep(1)
                # 登出
                logger.info('subprocesses done at 登出 for %s in %s' % (username, device_id))
                adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_LOGOUT_X, CONTINUOUS_BATTLE_BUTTON_LOGOUT_Y)
                sleep(2)
            elif "正常经营" in words:
                adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_AGREE_X, CONTINUOUS_BATTLE_BUTTON_AGREE_Y)
                sleep(1)
                # 我的
                logger.info('subprocesses done at 我的 for %s in %s' % (username, device_id))
                adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_MY_X, CONTINUOUS_BATTLE_BUTTON_MY_Y)
                sleep(1)
                # 登出
                logger.info('subprocesses done at 登出 for %s in %s' % (username, device_id))
                adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_LOGOUT_X, CONTINUOUS_BATTLE_BUTTON_LOGOUT_Y)
                sleep(2)
                # logger.info('subprocesses done at 退出app for %s in %s' % (username,device_id))
                # adb.quitApp(package_name)
                # sleep(3)
                # # adb.getAppStartTotalTime(component)
                # logger.info('subprocesses done at 启动一个Activity APP for %s in %s' % (username,device_id))
                # adb.startActivity(component)
                # sleep(3)
            else:
                # 我的
                logger.info('subprocesses done at 我的 for %s in %s' % (username, device_id))
                adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_MY_X, CONTINUOUS_BATTLE_BUTTON_MY_Y)
                sleep(2)
                # 登出
                logger.info('subprocesses done at 登出 for %s in %s' % (username, device_id))
                adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_LOGOUT_X, CONTINUOUS_BATTLE_BUTTON_LOGOUT_Y)
                sleep(2)
                # logger.info('subprocesses done at 退出app for %s in %s' % (username,device_id))
                # adb.quitApp(package_name)
                # sleep(3)
                # # adb.getAppStartTotalTime(component)
                # logger.info('subprocesses done at 启动一个Activity APP for %s in %s' % (username,device_id))
                # adb.startActivity(component)
                # sleep(3)
            # 我的
            logger.info('subprocesses done at 我的 for %s in %s' % (username, device_id))
            adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_MY_X, CONTINUOUS_BATTLE_BUTTON_MY_Y)
            # 登录
            logger.info('subprocesses done at 登录 for %s in %s' % (username, device_id))
            adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_LOGIN_X, CONTINUOUS_BATTLE_BUTTON_LOGIN_Y)
            # 输入
            logger.info('subprocesses done at 输入用户 for %s in %s' % (username, device_id))
            adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_INPUT_USERNAME_CLEAR_X,
                             CONTINUOUS_BATTLE_BUTTON_INPUT_USERNAME_CLEAR_Y)
            adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_INPUT_USERNAME_X, CONTINUOUS_BATTLE_BUTTON_INPUT_USERNAME_Y)
            adb.sendText(username)
            logger.info('subprocesses done at 输入密码 for %s in %s' % (username, device_id))
            adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_INPUT_PASSWORD_CLEAR_X,
                             CONTINUOUS_BATTLE_BUTTON_INPUT_PASSWORD_CLEAR_Y)
            adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_INPUT_PASSWORD_X, CONTINUOUS_BATTLE_BUTTON_INPUT_PASSWORD_Y)
            adb.sendText(password)
            # 向上滑动
            logger.info('subprocesses done at 向上滑动 for %s in %s' % (username, device_id))
            adb.swipeByCoord(CONTINUOUS_BATTLE_SWIPE_START_X, CONTINUOUS_BATTLE_SWIPE_START_Y, 0, 0)
            # 提交
            logger.info('subprocesses done at 提交 for %s in %s' % (username, device_id))
            adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_INPUT_SUBMIT_X, CONTINUOUS_BATTLE_BUTTON_INPUT_SUBMIT_Y)
            sleep(1)
            # 单位管理
            logger.info('subprocesses done at 单位管理 for %s in %s' % (username, device_id))
            adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_INPUT_MANAGER_X, CONTINUOUS_BATTLE_BUTTON_INPUT_MANAGER_Y)
            sleep(1)
            # 保存
            image_name = image_utils.screenShot()
            image_utils.writeToFile(os.path.join(base_photops, machine), image_name)
            sleep(1)
            image = image_utils.loadImage(os.path.join(base_photops, machine, image_name))
            sleep(1)
            logger.info('image width %s height %s' % (image.size[0], image.size[1]))
            words = image_utils.has_words(os.path.join(base_photops, machine, image_name),
                                                 CONTINUOUS_BATTLE_BUTTON_AGREE_CAT_START_X,
                                                 CONTINUOUS_BATTLE_BUTTON_AGREE_CAT_END_X,
                                                 CONTINUOUS_BATTLE_BUTTON_AGREE_CAT_START_Y,
                                                 CONTINUOUS_BATTLE_BUTTON_AGREE_CAT_END_Y)

            if "取消" in words:
                # 保存
                adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_INPUT_SAVE_X, CONTINUOUS_BATTLE_BUTTON_INPUT_SAVE_Y)
            # 培训考核
            logger.info('subprocesses done at 培训考核 for %s in %s' % (username, device_id))
            adb.swipeByCoord(CONTINUOUS_BATTLE_SWIPE_START_X, CONTINUOUS_BATTLE_SWIPE_START_Y, 0, 0)
            adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_INPUT_KAOHE_X, CONTINUOUS_BATTLE_BUTTON_INPUT_KAOHE_Y)

            for i in range(0, user.stage):
                # 向上滑动
                adb.swipeByCoord(0, 230, 0, 100)

            stage = 3 - user.stage
            for i in range(0, stage):
                # 向上滑动
                adb.swipeByCoord(0, 230, 0, 100)
                # 新办必学
                logger.info('subprocesses done at 新办必学 %s for %s in %s' % (i, username, device_id))
                adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_INPUT_XINBANBIXUE_X,
                                 CONTINUOUS_BATTLE_BUTTON_INPUT_XINBANBIXUE_Y)
                sleep(2)
                for j in range(0, user.step):
                    # 向上滑动
                    adb.swipeByCoord(CONTINUOUS_BATTLE_SWIPE_LIEBIAO_START_X, CONTINUOUS_BATTLE_SWIPE_LIEBIAO_START_Y,
                                     CONTINUOUS_BATTLE_SWIPE_LIEBIAO_END_X, CONTINUOUS_BATTLE_SWIPE_LIEBIAO_END_Y)
                    if j % 29 == 0:
                        sleep(2)

                j = user.step
                while True:
                    j += 1
                    # 列表
                    # 点击
                    logger.info('subprocesses done at 新办必学》点击 %s for %s in %s' % (j, username, device_id))
                    adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_LIEBIAO_X, CONTINUOUS_BATTLE_BUTTON_LIEBIAO_Y)
                    sleep(1)
                    while True:
                        adb.swipeByCoord(0, CONTINUOUS_BATTLE_SWIPE_LIEBIAO_START_Y * 2, 0, 0)
                        sleep(1)
                        image_name = image_utils.screenShot()
                        image_utils.writeToFile(os.path.join(base_photops, machine), image_name)
                        sleep(1)
                        image = image_utils.loadImage(os.path.join(base_photops, machine, image_name))
                        sleep(1)
                        logger.info('image width %s height %s' % (image.size[0], image.size[1]))
                        words = image_utils.has_words_paddle(os.path.join(base_photops, machine, image_name),
                                                             CONTINUOUS_SCREENCAP_START_X, CONTINUOUS_SCREENCAP_END_X,
                                                             CONTINUOUS_SCREENCAP_START_Y, CONTINUOUS_SCREENCAP_END_Y)
                        if "已学完100" in words:
                            break
                        logger.info('%s read video ...' % username)
                        adb.swipeByCoord(CONTINUOUS_BATTLE_SWIPE_LIEBIAO_START_X,
                                         CONTINUOUS_BATTLE_SWIPE_LIEBIAO_START_Y, CONTINUOUS_BATTLE_SWIPE_LIEBIAO_END_X,
                                         CONTINUOUS_BATTLE_SWIPE_LIEBIAO_END_Y)
                        sleep(60)
                    logger.info('user quantity step %s for %s in %s' % (j, username, device_id))
                    user_quantity_step(username)
                    logger.info('subprocesses done at 新办必学》点击返回 %s for %s in %s' % (j, username, device_id))
                    adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_BACK_X, CONTINUOUS_BATTLE_BUTTON_BACK_Y)
                    sleep(1)
                    adb.swipeByCoord(CONTINUOUS_BATTLE_SWIPE_LIEBIAO_START_X, CONTINUOUS_BATTLE_SWIPE_LIEBIAO_START_Y,
                                     CONTINUOUS_BATTLE_SWIPE_LIEBIAO_END_X, CONTINUOUS_BATTLE_SWIPE_LIEBIAO_END_Y)
                    if j % 29 == 0:
                        sleep(1)
                    sleep(1)
                    import random
                    random_integer = random.randint(1, 10)
                    if random_integer > 7:
                        image_name = image_utils.screenShot()
                        image_utils.writeToFile(os.path.join(base_photops, machine), image_name)
                        sleep(1)
                        image = image_utils.loadImage(os.path.join(base_photops, machine, image_name))
                        logger.info('底部截图 image width %s height %s' % (image.size[0], image.size[1]))
                        sleep(1)
                        words = image_utils.has_words(os.path.join(base_photops, machine, image_name))
                        if "没有更多数据了" in words:
                            break
                logger.info('user quantity stage %s for %s in %s' % (i, username, device_id))
                user_quantity_stage(username)
                adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_BACK_X, CONTINUOUS_BATTLE_BUTTON_BACK_Y)
                sleep(1)
            user_delete(username)
        except Exception as ex:
            logger.error('subprocesses done for run for %s' % device_id)
            logger.error(str(ex))
            raise ex
        finally:
            # 我的
            logger.info('subprocesses done at 我的 for %s in %s' % (username, device_id))
            adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_MY_X, CONTINUOUS_BATTLE_BUTTON_MY_Y)
            # 登出
            logger.info('subprocesses done at 登出 for %s in %s' % (username, device_id))
            adb.touchByRatio(CONTINUOUS_BATTLE_BUTTON_LOGOUT_X, CONTINUOUS_BATTLE_BUTTON_LOGOUT_Y)
            logger.info('subprocesses done at 退出app for %s in %s' % (username, device_id))
            adb.quitApp(package_name)


class InitBasedAction(AbstractAction, ABC):
    """
    HandleBasedAttacher implemented common handle (hWnd) based IPC interaction with specified handle through WINAPI
    """

    def __init__(self, host: Optional[str] = '127.0.0.1', num: Optional[int] = 4, first: Optional[int] = 16384):
        self.host = host
        self.num = num
        self.first = first
        self.handle = LazyValue(self.locate_handle)

    def locate_handle(self):
        """
        Locate the simulator handle, used for screenshot capturing and message sending

        :return: The handle of the simulator, if not found, returns 0
        """
        workers = [loop_executor.create_event_loop_thread(AbstractAction.init, self.host + ':' + str(i)) for i in
                   self.get_ports()]
        loop_executor.exetute(*workers, wait=True)
        auto_setup(__file__)
        logger.info('All subprocesses done for init')


class RunAction(AbstractAction, ABC):
    """
    HandleBasedAttacher implemented common handle (hWnd) based IPC interaction with specified handle through WINAPI
    """

    def __init__(self, host: Optional[str] = '127.0.0.1', num: Optional[int] = 4, first: Optional[int] = 16384):
        self.host = host
        self.num = num
        self.first = first
        self.handle = LazyValue(self.locate_handle)

    def locate_handle(self):
        """
        Locate the simulator handle, used for screenshot capturing and message sending

        :return: The handle of the simulator, if not found, returns 0
        """
        from collections import deque, defaultdict
        users = [_user.dict() for _user in user_all()]
        ports = self.get_ports().tolist()
        size = len(ports)
        for index, user in enumerate(users):
            port = str(ports[index % size])
            device_id = self.host + ':' + str(port)
            user.update({"device_id": device_id, "host": self.host, "port": port})

        data_groups = defaultdict(list)
        for item in users:
            key = item['device_id']
            data_groups[key].append(item)

        # workers = [loop_executor.create_event_loop_thread(AbstractAction.run , user) for user in users]
        # loop_executor.exetute(*workers, wait=True)

        while True:
            data_groups = func.multiprocessing_group(
                items=data_groups,
                function=collect,
                chunks=1,
            )
            if len(data_groups) == 0:
                break

        auto_setup(__file__)
        logger.info('All subprocesses done for run')


def collect(index, items, return_dict):
    ''' dummy function to return values '''
    local_items = []
    logger.warning("dummy function to return values")
    logger.error(local_items)
    while True:
        for item in items:
            try:
                AbstractAction.run(item)
            except Exception as ex:
                logger.error('subprocesses done error for %s' % json.dumps(item))
                local_items.append(item)
        if len(local_items) > 0:
            return_dict[index] = local_items
        if len(local_items) == 0:
            break
        logger.warning("dummy function to return values")
        logger.error(local_items)
        items = local_items
