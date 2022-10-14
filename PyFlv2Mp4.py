# 不解码转化flv文件
# ffmpeg -i "%%~a" -vcodec copy -f mp4 "%%~na.mp4"

# 检测完整性

# 删除FLV文件

# 过滤出所有flv文件

# 判断解码里含有 bilibili 字样???
from argparse import ArgumentError
from configparser import ConfigParser
import os
import pathlib
import datetime
import re


def pyinstaller_getcwd():
    import os
    import sys
    # determine if the application is a frozen `.exe` (e.g. pyinstaller --onefile)
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    # or a script file (e.g. `.py` / `.pyw`)
    elif __file__:
        application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path


def get_config_file() -> str:
    config_file = 'PyFlv2Mp4.config.ini'
    app_dir = pyinstaller_getcwd()
    return os.path.join(app_dir, config_file)


def is_portable_mode() -> bool:
    cwd = pyinstaller_getcwd()
    allfiles = os.listdir(cwd)
    files = [fname for fname in allfiles if "readme" in fname.lower()]
    return len(files) < 1


def check_ffmpeg_exist() -> bool:
    import shutil
    return (shutil.which("ffmpeg") is not None)


def human_readable_size(size: int, decimal_places=2) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"


def isFileExist(folder: str, filename: str) -> bool:
    file_path = os.path.join(folder, filename)
    return os.path.exists(file_path)


def IsStringNullOrEmpty(value: str):
    return value is None or len(value) == 0


def save_to_history(file_path: str):
    try:
        history_filename = "convert.history.txt"
        app_dir = pyinstaller_getcwd()
        history_file = os.path.join(app_dir, history_filename)
        timestamp = datetime.datetime.strftime(
            datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        str_write_to_file = f"{timestamp}: converted:\n   {file_path}\n"
        if (os.path.exists(history_file)):
            with open(history_file, 'a') as f:
                f.write(str_write_to_file)
        else:
            with open(history_file, 'w') as f:
                f.write(str_write_to_file)
    except:
        pass


def check_integrity_of_video(download_path: str, video_file: str, callback_to_delete, err_callback):
    # ffmpeg_cmd = f'ffmpeg -v error -i "[YouTube][1080P]Yoga - Gymnastics with Lera.mp4" -f null - >error.log 2>&1'
    # ffmpeg_cmd = f' cd /d "{download_path}" && ffmpeg -v error -i "{video_file}" -f null - '
    # cmd_keep = f'cmd /c "{ffmpeg_cmd}"'
    # os.system(cmd_keep)
    import subprocess
    # run_ret = subprocess.call(
    #     ['ffmpeg', '-v', 'error', '-i', f'{video_file}', '-f', 'null', '-'], cwd=download_path)
    if (isFileExist(download_path, video_file)):
        print(f"> Start checking video file integrity with ffmpeg...")
        # ffmpeg -hide_banner -v warning -stats -i
        run_ret_output = subprocess.check_output(
            ['ffmpeg', '-v', 'error', '-i', f'{video_file}', '-f', 'null', '-'], cwd=download_path, stderr=subprocess.STDOUT, text=True)  # , shell=True
        if (len(run_ret_output) != 0):
            print(
                f"! Video file is incomplete: \n    {video_file}\n! Error detail:\n{run_ret_output}! Error detail^^^")
            err_callback()

        else:
            # intput_keys = input(
            #     'Video file is complete, do you want to delete intermediate files? \n  Press Y to DELETE, otherwise CANCEL: ')
            # if (len(intput_keys) > 0):
            #     input_char = intput_keys[0]
            #     if (input_char.lower() == 'y'):
            #         print(f'> Deleting intermediate files...')
            #         callback_to_delete()
            #     else:
            #         print("Your choise is: DO NOTHING.")
            # else:
            #     print("Your choise is: DO NOTHING.")
            print("> Video file is complete, deleting intermediate file...")
            callback_to_delete()
        print(f"> Check video file integrity with ffmpeg ends.")


def clear_intermediate_files(download_path: str, video_file: str):
    try:
        video = os.path.join(download_path, video_file)
        os.remove(video)
        print(f"  deleted intermediate file: {video_file}")
    except:
        pass


def mark_as_tried_but_failed(filename: str) -> str:
    return f'[ConvertFailed]{filename}'


def has_tried_but_failed(filename: str) -> bool:
    ret = "failed]" in filename.lower()
    if (ret):
        print(
            f"! Tried to convert this flv to mp4 but failed, please convert manually:\n    {filename}")
    return ret


def clear_error_output_and_mark_failed_to_source_file(download_path: str, source_file: str, err_output: str):
    try:
        video = os.path.join(download_path, err_output)
        os.remove(video)
        print(f"  deleted error output file: {err_output}")
        os.rename(os.path.join(download_path, source_file),
                  os.path.join(download_path, mark_as_tried_but_failed(source_file)))
    except:
        pass


def get_download_path_not_none(download_path: str, config_file: str):
    if (not pathlib.Path(download_path).exists()):
        if os.name == "nt":
            download_path = f"{os.getenv('USERPROFILE')}\\Downloads"
        else:  # PORT: For *Nix systems
            download_path = f"{os.getenv('HOME')}/Downloads"
        print(
            f'\n!  WARNING: STRONGLY RECOMMENDED TO SPECIFY YOUR download_path in "{config_file}"\n    Now use "{download_path}"')
        save_download_path_to_config(download_path, config_file)
    print(f"> download_path = {download_path}")
    return download_path


def save_download_path_to_config(download_path: str, config_file: str):
    config = ConfigParser()
    if (os.path.exists(config_file)):
        try:
            with open(config_file) as f:
                config.read_file(f)
            config.set('Settings', 'download_path', download_path)
            with open(config_file, 'w') as f:
                config.write(f)
        except Exception as e:
            print(f"! {str(e)}")


def get_download_path(config_file: str):
    config = ConfigParser()
    if (os.path.exists(config_file)):
        try:
            with open(config_file) as f:
                config.read_file(f)
                return get_download_path_not_none(config['Settings']['download_path'], config_file)
        except:
            return get_download_path_not_none("ERROR_OCCUR", config_file)
    else:
        config.add_section('Settings')
        config['Settings']['download_path'] = "NOT_SET"
        with open(config_file, 'w') as f:
            config.write(f)
    return get_download_path_not_none("NOT_SET", config_file)


def find_all_flv_files(dir: str) -> list[str]:
    allfiles = os.listdir(dir)
    files = [fname for fname in allfiles if fname.lower().endswith(".flv")]
    return files


def get_file_basename(download_path: str, filename: str) -> str:
    base = os.path.basename(os.path.join(download_path, filename))
    return os.path.splitext(base)[0]


def check_video_file_valid(folder: str, video_file: str):
    try:
        file_path = os.path.join(folder, video_file)
        if (not os.path.exists(file_path)):
            return False
        file_size = os.path.getsize(file_path)
        ret = file_size > 100 * 1024  # 200KB
        if (not ret):
            print(
                f"! Video file[{file_size} bytes] less than 100KB. error, deleted for you:\n    {video_file}")
            os.remove(file_path)
        return ret
    except:
        return False


def convert_flv_to_mp4(download_path: str, flv_file: str):
    if (not check_video_file_valid(download_path, flv_file) or has_tried_but_failed(flv_file)):
        return
    output_file = f"{get_file_basename(download_path, flv_file)}.mp4"
    try:
        if (isFileExist(download_path, output_file)):
            print(
                f"> Output(mp4) file already exists:\n    {output_file}")
            return

        if (check_ffmpeg_exist()):
            ffmpeg_cmd = f' cd /d "{download_path}" && ffmpeg -hide_banner -v warning -stats -i "{flv_file}" -vcodec copy -f mp4 "{output_file}" '
            # cmd /c, 不留在cmd命令可能切换的文件夹, /k留在(执行后,工作路径可能改变)
            cmd_keep = f'cmd /c "{ffmpeg_cmd}"'
            print(
                f"\n> Start to convert FLV to MP4 with ffmpeg:\n    {flv_file}")
            os.system(cmd_keep)
            check_integrity_of_video(
                download_path, output_file,
                lambda: clear_intermediate_files(download_path, flv_file), lambda: clear_error_output_and_mark_failed_to_source_file(download_path, flv_file, output_file))

            if (isFileExist(download_path, output_file)):
                print(f"> Convert video ends, output file:\n    {output_file}")
                if (not is_portable_mode()):
                    save_to_history(os.path.join(download_path, output_file))

        else:
            ffmpeg_download_url = "https://ffmpeg.org/download.html"
            print(
                f"!  ffmpeg.exe not exist, please download ffmpeg and set to PATH, then combine video and audio files by yourself:\n    {ffmpeg_download_url}\n")
        # os.system(f'cmd /c "cd /d {os.getcwd()}"')
        # import pyperclip
        # pyperclip.copy(ffmpeg_cmd)
        # print(
        #     f'> The following command has been copied to the clipboard, please run it in the terminal with ffmpeg\n    {ffmpeg_cmd}')
    except Exception as e:
        print(f"!  {str(e)}")


def main():
    print("*** PyFlv2Mp4 version 1.0.1 Copyright (c) 2022 Carlo R. All Rights Reserved. ***")
    print("*** Contact us at uvery6@gmail.com ")
    print("* Convert flv to mp4 without transcoding, design for bilibili")
    print("> START...")
    if (is_portable_mode()):
        download_path = pyinstaller_getcwd()
    else:
        config_file = get_config_file()
        print(f"> You could configure software in:\n    {config_file}")
        download_path = get_download_path(config_file)

    # if (youtube_url == None or len(youtube_url) < 8):
    #     print('\n!  ERROR: MUST SPECIFY youtube_url in "config.ini"\n')
    #     return

    li = find_all_flv_files(download_path)
    if (len(li) < 1):
        print(f"\n> No flv file need to be converted to mp4.\n")
    else:
        for flv_file in li:
            convert_flv_to_mp4(download_path, flv_file)


if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        if ("HTTP Error 429: Too Many Requests" in str(e)):
            print(f"\n!  HTTP Error 429: Too Many Requests to Youtube: You should change your IP address via VPN.\n")
        else:
            # import sys
            # print(sys.exc_info()[0])
            import traceback
            print(f"!  {traceback.format_exc()}")
    finally:
        print("Press Enter to exit...")
        input()
