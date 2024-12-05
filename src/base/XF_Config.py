import json
from os.path import abspath


class Config:
    """
    配置管理类，提供只读动态配置管理，支持单例模式。
    """
    _instance = None  # 单例实例
    _initialized = None

    def __new__(cls, *args, **kwargs):
        """
        单例模式，确保全局只有一个实例。
        """
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.config = None  # 初始化配置为空
        return cls._instance

    @classmethod
    def init(cls, config_file=None):
        """
        初始化配置，仅允许初始化一次。
        """
        instance = cls()
        if instance._initialized:
            raise RuntimeError("配置已经初始化，禁止重复初始化！")
        if config_file:
            cls.config_file = abspath(config_file)
            instance.loadFromFile(cls.config_file)
            instance._initialized = True
        else:
            raise ValueError("必须提供配置文件路径进行初始化。")

    @property
    def EditorConfig(self):
        """
        返回当前EditorConfig配置，确保配置已被加载。
        """
        if self.config is None:
            raise ValueError("配置尚未初始化，请调用 init() 方法加载配置。")
        if self.config.get("EditorConfig") is None:
            raise ValueError("配置文件中缺少 EditorConfig 部分。")
        return self.config["EditorConfig"]

    @property
    def NodeConfig(self):
        """
        返回当前NodeConfig配置，确保配置已被加载。
        """
        if self.config is None:
            raise ValueError("配置尚未初始化，请调用 init() 方法加载配置。")
        if self.config.get("NodeConfig") is None:
            raise ValueError("配置文件中缺少 NodeConfig 部分。")
        return self.config["NodeConfig"]

    @property
    def PinConfig(self):
        """
        返回当前NodeConfig配置，确保配置已被加载。
        """
        if self.config is None:
            raise ValueError("配置尚未初始化，请调用 init() 方法加载配置。")
        if self.config.get("PinConfig") is None:
            raise ValueError("配置文件中缺少 PinConfig 部分。")
        return self.config["PinConfig"]

    @property
    def GroupConfig(self):
        """
        返回当前GroupConfig配置，确保配置已被加载。
        """
        if self.config is None:
            raise ValueError("配置尚未初始化，请调用 init() 方法加载配置。")
        if self.config.get("GroupConfig") is None:
            raise ValueError("配置文件中缺少 GroupConfig 部分。")
        return self.config["GroupConfig"]

    def loadFromFile(self, file_path):
        """
        从 JSON 文件加载动态配置，支持错误处理。
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            self.config_file = file_path
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件未找到：{file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"配置文件格式错误：{file_path}")

    def reload(self):
        """
        重新加载配置文件，覆盖当前配置。
        """
        self.loadFromFile(self.config_file)
        print(f"配置文件 {self.config_file} 已重新加载。")


if __name__ == "__main__":
    config = Config()
    config.init("config.json")
    print(config.config)
