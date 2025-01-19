import os
import shutil

class DataPathTransfer:
    def __init__(self, env, str_folder, count=1):
        self.env = env
        self.count = count
        self.new_path_folder = str_folder
        self.old_paths = self._construct_old_paths()
        self.new_paths = self._construct_new_paths()

    def _construct_old_paths(self):
        path_out = f"{self.new_path_folder}/{self.env['start_date']}_{self.env['end_date']}"
        return {
            "ev": f"out_stock/Training_result/{path_out}/{self.count}/{self.env['stock_id']}/ev"
        }

    def _construct_new_paths(self):
        return {
            "ev": f"out_stock/Training_result/{self.new_path_folder}/{self.count}/{self.env['start_date']}_{self.env['end_date']}/{self.env['stock_id']}/ev"
        }

    def transfer_files(self):
        for key, old_path in self.old_paths.items():
            new_path = self.new_paths[key]
            os.makedirs(os.path.dirname(new_path), exist_ok=True)

            if os.path.exists(old_path):
                if os.path.isfile(old_path):
                    # 若是檔案，使用 copyfile
                    shutil.copyfile(old_path, new_path)
                    print(f"Copied file: {old_path} to {new_path}")
                elif os.path.isdir(old_path):
                    # 若是目錄，使用 copytree
                    shutil.copytree(old_path, new_path, dirs_exist_ok=True)
                    print(f"Copied directory: {old_path} to {new_path}")
            else:
                print(f"File or directory not found: {old_path}")
                
                
# Write this in run.ipynb
# from data_path_transfer2 import DataPathTransfer

# for stock in data:
#     list_date, list_bnh_rtn, list_stag_rtn  = [], [], []
#     for date_range in date_ranges:
#         env = {
#             "stock_id" : stock[0],
#             "stock_name" : stock[1],
#             "country" : stock[2],
#             "start_date" : date_range[0],
#             "end_date" : date_range[1],
#         }
        
#         for i in range(1,11):
#             converter = DataPathTransfer(env, "Embd", i)
#             converter.transfer_files()