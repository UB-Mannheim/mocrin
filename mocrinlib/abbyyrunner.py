import shlex
import subprocess
from mocrinlib.common import create_dir


def start_abbyy(file, path_out):
    create_dir(path_out)
    file_out = path_out + file.split('/')[-1]+".xml"
    parameters = f"-if {file} -recc -f XML -xcam Ascii -of {file_out}"
    parameters = shlex.split(parameters)
    subprocess.Popen(args=['abbyyocr11']+parameters).wait()
    return