# run_02 数值复现

在 PowerShell 中执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& 'C:\Users\admin\miniconda3\shell\condabin\conda-hook.ps1'
conda activate phasefield
python .\run_analysis.py --data-dir ..\..\raw\prob25B --project ..
python -m unittest -v .\test_physics.py
```

`run_analysis.py` 只读取官方四个附件，输出写入 `output/`、`tables/` 与 `figures/`。`--quick` 用于流程冒烟测试；论文登记值必须来自不带该参数的完整运行。
