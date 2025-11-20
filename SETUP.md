# 环境变量设置指南

## 方法1：使用setup_env.bat（Windows）

运行以下命令：
```bash
setup_env.bat
```

然后按照提示输入环境变量。

## 方法2：手动创建.env文件

在项目根目录创建 `.env` 文件，内容如下：

```env
# OpenAI API Key
OPENAI_API_KEY=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

# Smithery API Configuration
SMITHERY_API_KEY=30a5c47c-fdc7-4c7a-bc30-d1b99b1c89f9
SMITHERY_PROFILE_ID=enchanting-finch-Fj3QCf

# Flask Secret Key (change in production)
SECRET_KEY=your-secret-key-here
```

## 环境变量说明

- **OPENAI_API_KEY**: OpenAI API密钥，用于生成Pandas代码
- **SMITHERY_API_KEY**: Smithery API密钥（可选，用于远程沙箱执行）
- **SMITHERY_PROFILE_ID**: Smithery配置文件ID（可选）
- **SECRET_KEY**: Flask会话密钥，生产环境请更改

## 验证设置

运行以下命令验证环境变量是否正确加载：
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```





