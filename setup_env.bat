@echo off
echo Creating .env file...
echo.

REM 直接设置变量值
REM OpenAI API Key for GPT-4
set OPENAI_API_KEY=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

REM OpenRouter API Key for other models (Llama, Gemini, Qwen)
set OPENROUTER_API_KEY=sk-or-v1-a449cfec710b847c7a6017ccefa47204ee766b5d8ba1a0b18816d7c5c40ea75

REM Smithery Configuration
set SMITHERY_API_KEY=30a5c47c-fdc7-4c7a-bc30-d1b99b1c89f9
set SMITHERY_PROFILE_ID=enchanting-finch-Fj3QCf

REM Flask Secret Key
set SECRET_KEY=dev-secret-key-change-in-production

REM 直接写入.env文件
(
echo # OpenAI API Key for GPT-4
echo OPENAI_API_KEY=%OPENAI_API_KEY%
echo.
echo # OpenRouter API Key for other models
echo OPENROUTER_API_KEY=%OPENROUTER_API_KEY%
echo.
echo # Smithery API Configuration
echo SMITHERY_API_KEY=%SMITHERY_API_KEY%
echo SMITHERY_PROFILE_ID=%SMITHERY_PROFILE_ID%
echo.
echo # Flask Secret Key
echo SECRET_KEY=%SECRET_KEY%
) > .env

echo.
echo .env file created successfully!
echo.
echo Verifying .env file contents:
type .env
echo.

