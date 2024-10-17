import pyrealsense2 as rs
import numpy as np
import cv2

class RealSenseVideoCapture:
    def __init__(self, serial_number=None, width=640, height=480, fps=30, is_depth_camera=False):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.width = width
        self.height = height
        self.fps = fps
        self.serial_number = serial_number

        # カメラのシリアル番号を指定する場合
        if serial_number is not None:
            self.config.enable_device(serial_number)

        # ストリームの設定
        if is_depth_camera:
            self.config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
        else:
            self.config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)

        # パイプラインの開始
        self.pipeline.start(self.config)
        if not self.pipeline.is_started():
            raise Exception("Pipeline could not be started.")
        self.align = rs.align(rs.stream.color)
        self.running = True

        # センサーオプションの取得
        self.profile = self.pipeline.get_active_profile()
        self.sensor = self.profile.get_device().first_color_sensor()

    def read(self):
        if not self.running:
            return False, None
        
        try:
            # フレームの取得
            frames = self.pipeline.wait_for_frames()
            aligned_frames = self.align.process(frames)
            color_frame = aligned_frames.get_color_frame()

            if not color_frame:
                return False, None

            # 画像データを NumPy 配列に変換
            color_image = np.asanyarray(color_frame.get_data())
            return True, color_image
        except Exception as e:
            print(f"Error: {e}")
            return False, None

    def release(self):
        # リソースを解放
        self.pipeline.stop()
        self.running = False

    def isOpened(self):
        return self.running

    def set(self, prop_id, value):
        try:
            # カメラ設定の変更
            if prop_id == cv2.CAP_PROP_FRAME_WIDTH:
                self.width = int(value)
                self.config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, self.fps)
            elif prop_id == cv2.CAP_PROP_FRAME_HEIGHT:
                self.height = int(value)
                self.config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, self.fps)
            elif prop_id == cv2.CAP_PROP_FPS:
                self.fps = int(value)
                self.config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, self.fps)
            elif prop_id == cv2.CAP_PROP_AUTO_EXPOSURE:
                self.sensor.set_option(rs.option.enable_auto_exposure, bool(value))
            elif prop_id == cv2.CAP_PROP_EXPOSURE:
                self.sensor.set_option(rs.option.exposure, value)
            elif prop_id == cv2.CAP_PROP_AUTO_WB:
                self.sensor.set_option(rs.option.enable_auto_white_balance, bool(value))
            elif prop_id == cv2.CAP_PROP_WHITE_BALANCE_BLUE_U:
                self.sensor.set_option(rs.option.white_balance, value)
            else:
                print(f"Property ID {prop_id} not supported.")
                return False
            return True
        except Exception as e:
            print(f"Error setting property: {e}")
            return False

    def get(self, prop_id):
        try:
            # カメラ設定の取得
            if prop_id == cv2.CAP_PROP_FRAME_WIDTH:
                return self.width
            elif prop_id == cv2.CAP_PROP_FRAME_HEIGHT:
                return self.height
            elif prop_id == cv2.CAP_PROP_FPS:
                return self.fps
            elif prop_id == cv2.CAP_PROP_AUTO_EXPOSURE:
                return self.sensor.get_option(rs.option.enable_auto_exposure)
            elif prop_id == cv2.CAP_PROP_EXPOSURE:
                return self.sensor.get_option(rs.option.exposure)
            elif prop_id == cv2.CAP_PROP_AUTO_WB:
                return self.sensor.get_option(rs.option.enable_auto_white_balance)
            elif prop_id == cv2.CAP_PROP_WHITE_BALANCE_BLUE_U:
                return self.sensor.get_option(rs.option.white_balance)
            else:
                print(f"Property ID {prop_id} not supported.")
                return None
        except Exception as e:
            print(f"Error getting property: {e}")
            return None

