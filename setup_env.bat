@echo off
echo Creating .env file...
echo.

REM 直接设置变量值
REM OpenAI API Key for GPT-4
set OPENAI_API_KEY= youself
REM OpenRouter API Key for other models (Llama, Gemini, Qwen)
set OPENROUTER_API_KEY= youself

REM Smithery Configuration
set SMITHERY_API_KEY= youself
set SMITHERY_PROFILE_ID= youself

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

