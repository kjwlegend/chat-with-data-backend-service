from pathlib import Path
from dotenv import load_dotenv

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent

# 加载环境变量
load_dotenv(ROOT_DIR / ".env")


