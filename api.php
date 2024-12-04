<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$response = [
    'version' => '1.0.1',  // 当前最新版本号
    'update_url' => 'https://blog.biekanle.com/software/1255.html',  // 更新下载地址
    'force_update' => false,  // 是否强制更新
    'update_msg' => '新版本更新内容：\n1. 修复已知bug\n2. 优化用户体验'  // 更新说明
];

echo json_encode($response);
?>