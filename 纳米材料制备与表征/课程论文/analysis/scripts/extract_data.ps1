# 从各实验目录的原始压缩包解压分析所需数据到 analysis/data（可重复执行）
$base = "E:\latex_AI\纳米材料制备与表征"
$dst  = Join-Path $PSScriptRoot "..\data"
New-Item -ItemType Directory -Force -Path $dst | Out-Null

$jobs = @(
    @{ Zip = "$base\X射线粉末衍射\XRD数据\第五组.zip";     Out = "$dst\xrd\g5" },
    @{ Zip = "$base\X射线粉末衍射\XRD数据\第六组.zip";     Out = "$dst\xrd\g6" },
    @{ Zip = "$base\X射线粉末衍射\XRD数据\第一组XRD.zip";  Out = "$dst\xrd\g1" },
    @{ Zip = "$base\X射线粉末衍射\XRD数据\第三组XRD.zip";  Out = "$dst\xrd\g3" },
    @{ Zip = "$base\拉曼散射\拉曼光谱.zip";                Out = "$dst\raman" },
    @{ Zip = "$base\分光光度计\分光光度计(1).zip";         Out = "$dst\uvvis" },
    @{ Zip = "$base\扫描电子显微镜\SEM专业实验-2024级（包含EDS）(1).zip"; Out = "$dst\sem" }
)

foreach ($j in $jobs) {
    if (Test-Path -LiteralPath $j.Zip) {
        Write-Output ("extracting " + [System.IO.Path]::GetFileName($j.Zip))
        Expand-Archive -LiteralPath $j.Zip -DestinationPath $j.Out -Force
    } else {
        Write-Output ("missing: " + $j.Zip)
    }
}
Write-Output "done -> $dst"
