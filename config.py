# -----------------大目标App--------------------------------
import os
base_photops="D:\\sdcard"
package_name = 'com.mysd.sunnycafeteria'
activity = '.MainActivity'

current_dir = os.path.dirname(os.path.realpath(__file__))
apk_file = os.path.join(current_dir, "data","com.mysd.sunnycafeteria.apk")
user_info_file = os.path.join(current_dir, "data","user.info")
db_file = os.path.join(current_dir, "data","database.db")