[English](README.md) | **简体中文**

# LeoClaw

一个小型 ReAct 编程 Agent 命令行工具，使用 LangChain 模型适配和工具调用，在指定目录中读写文件、搜索和执行命令。当前是显式 Python Agent 循环，运行依赖不包含 LangGraph。

## 安装与配置

要求 Python 3.10 或更新版本。在 PowerShell 中：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

在 `.env` 设置 `MODEL_PROVIDER=deepseek` 和 `DEEPSEEK_API_KEY`，或者使用 `MODEL_PROVIDER=openai` 与 `OPENAI_API_KEY`。可选模型配置参照 `.env.example`，以账号可用模型为准，勿提交密钥。

## 运行与开发

```powershell
leoclaw "Create a hello.py script" --workspace .\demo
pytest
```

未指定目录时创建当前目录下的 `.leoclaw-workspace`。终端打印工具活动及最终答复。代码位于 `src/leoclaw/`，测试位于 `tests/`。

文件和搜索工具检查解析后的路径，阻止越出工作目录；Shell 子进程不是操作系统沙箱，请使用可信任务和目录。Windows 包含纯 Python 哈希回退以兼容阻止未签名 `xxhash` 扩展的环境。

## 作者与许可证

作者/维护者：[https://github.com/OOOHGOD](https://github.com/OOOHGOD)。

原创贡献采用 [MIT 许可证](LICENSE)，允许商用和修改；分发软件副本或实质部分时须保留版权与许可声明。第三方代码、数据、模型和媒体素材保留各自权利，详见 [LICENSE_SCOPE.md](LICENSE_SCOPE.md)。
