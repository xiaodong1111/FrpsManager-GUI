@echo off
echo 开始打包程序...
pyinstaller frps_gui.spec
echo 打包完成！
echo 生成的文件在 dist 目录中
pause 