import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "file:///C:/Users/rog/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const inputPath = process.argv[2];
const outputDir = process.argv[3];
const payload = JSON.parse(await fs.readFile(inputPath, "utf8"));
await fs.mkdir(outputDir, { recursive: true });

function colName(index) {
  let n = index + 1;
  let text = "";
  while (n > 0) {
    const rem = (n - 1) % 26;
    text = String.fromCharCode(65 + rem) + text;
    n = Math.floor((n - 1) / 26);
  }
  return text;
}

function styleSheet(sheet, rows, cols) {
  const last = colName(cols - 1);
  const used = sheet.getRange(`A1:${last}${rows}`);
  sheet.showGridLines = false;
  used.format.font = { name: "Microsoft YaHei", size: 10, color: "#222222" };
  sheet.getRange(`A1:${last}1`).format = {
    fill: "#1F4E78",
    font: { name: "Microsoft YaHei", size: 10, bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
  };
  used.format.borders = { preset: "all", style: "thin", color: "#D9E2F3" };
  used.format.autofitColumns();
  sheet.getRange(`A1:${last}1`).format.rowHeight = 34;
  sheet.freezePanes.freezeRows(1);
}

async function writeWorkbook(fileName, tables) {
  const wb = Workbook.create();
  for (const [index, [name, rows]] of Object.entries(tables).entries()) {
    if (!rows || rows.length === 0) continue;
    const sheet = wb.worksheets.add(name.slice(0, 31) || `数据${index + 1}`);
    sheet.getRangeByIndexes(0, 0, rows.length, rows[0].length).values = rows;
    styleSheet(sheet, rows.length, rows[0].length);
  }
  const xlsx = await SpreadsheetFile.exportXlsx(wb);
  await xlsx.save(path.join(outputDir, fileName));
}

function rowsFromTable(key) {
  const table = payload["表格"][key];
  return table.slice(1).map((row) => row.map((value) => Number(value)));
}

function histogram(values, bins = 24) {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = Math.max(max - min, 1e-12);
  const step = span / bins;
  const counts = Array.from({ length: bins }, () => 0);
  for (const value of values) {
    const index = Math.min(bins - 1, Math.floor((value - min) / step));
    counts[index] += 1;
  }
  return counts.map((count, index) => [min + (index + 0.5) * step, count]);
}

function ecdf(values) {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted.map((value, index) => [value, (index + 1) / sorted.length]);
}

function meanByBins(x, y, bins = 60) {
  const min = Math.min(...x);
  const max = Math.max(...x);
  const step = (max - min) / bins;
  const sums = Array.from({ length: bins }, () => 0);
  const counts = Array.from({ length: bins }, () => 0);
  for (let i = 0; i < x.length; i += 1) {
    const index = Math.min(bins - 1, Math.floor((x[i] - min) / step));
    sums[index] += y[i];
    counts[index] += 1;
  }
  return {
    centers: Array.from({ length: bins }, (_, i) => min + (i + 0.5) * step),
    means: sums.map((sum, i) => (counts[i] ? sum / counts[i] : null)),
  };
}

const fit10 = rowsFromTable("10度实测与模型拟合");
const fit15 = rowsFromTable("15度实测与模型拟合");
const raw10 = rowsFromTable("附件1_10度原始光谱");
const raw15 = rowsFromTable("附件2_15度原始光谱");
const residual10 = rowsFromTable("10度模型拟合残差");
const residual15 = rowsFromTable("15度模型拟合残差");
const y10 = fit10.map((row) => row[1]);
const y15 = fit15.map((row) => row[1]);
const e10 = residual10.map((row) => row[1]);
const e15 = residual15.map((row) => row[1]);

const allTables = {};
const chartFiles = [];
function addChart(fileName, description, originType, rows, sheetName) {
  allTables[sheetName] = rows;
  chartFiles.push({ fileName, sheetName, description, originType, columns: rows[0] });
}

addChart(
  "01_10度原始光谱.xlsx",
  "查看10度全波段反射率变化和边界异常点",
  "折线图",
  [["波数(cm^-1)-X", "反射率(小数)-Y"], ...raw10],
  "01_10度原始光谱",
);
addChart(
  "02_15度原始光谱.xlsx",
  "查看15度全波段反射率变化和边界异常点",
  "折线图",
  [["波数(cm^-1)-X", "反射率(小数)-Y"], ...raw15],
  "02_15度原始光谱",
);

function agreementTable(rows) {
  const observed = rows.map((row) => row[1]);
  const fitted = rows.map((row) => row[2]);
  const low = Math.min(...observed, ...fitted);
  const high = Math.max(...observed, ...fitted);
  return [
    ["实测反射率-X", "模型拟合反射率-Y", "理想一致线-X2", "理想一致线-Y2"],
    ...rows.map((row) => [row[1], row[2], null, null]),
    [null, null, low, low],
    [null, null, high, high],
  ];
}
addChart(
  "03_10度实测模型一致性.xlsx",
  "用散点和一比一参考线检查10度拟合是否系统偏离",
  "散点图+参考线",
  agreementTable(fit10),
  "03_10度一致性散点",
);
addChart(
  "04_15度实测模型一致性.xlsx",
  "用散点和一比一参考线检查15度拟合是否系统偏离",
  "散点图+参考线",
  agreementTable(fit15),
  "04_15度一致性散点",
);

addChart(
  "05_绝对残差散点.xlsx",
  "比较两个角度的误差幅度随波数的变化",
  "散点图",
  [
    ["波数(cm^-1)-X", "10度绝对残差-Y", "15度绝对残差-Y2"],
    ...fit10.map((row, i) => [row[0], Math.abs(e10[i]), Math.abs(e15[i])]),
  ],
  "05_绝对残差散点",
);

const h10 = histogram(e10);
const h15 = histogram(e15);
addChart(
  "06_残差直方图.xlsx",
  "比较两个角度残差的集中区间和偏斜方向",
  "直方图",
  [
    ["残差区间中心-X", "10度频数-Y", "15度频数-Y2"],
    ...h10.map((row, i) => [row[0], row[1], h15[i][1]]),
  ],
  "06_残差直方图",
);

addChart(
  "07_残差箱线图.xlsx",
  "用箱线图比较两个角度残差的中位数、四分位距和异常点",
  "箱线图",
  [
    ["样本序号-X", "10度残差-Y", "15度残差-Y2"],
    ...Array.from({ length: Math.max(e10.length, e15.length) }, (_, i) => [i + 1, e10[i] ?? null, e15[i] ?? null]),
  ],
  "07_残差箱线图",
);

const b10 = meanByBins(fit10.map((row) => row[0]), e10);
const b15 = meanByBins(fit15.map((row) => row[0]), e15);
addChart(
  "08_残差热力图.xlsx",
  "按波数分箱观察10度与15度残差的共同系统结构",
  "热力图",
  [
    ["入射角\\波数", ...b10.centers],
    ["10度", ...b10.means],
    ["15度", ...b15.means],
  ],
  "08_残差热力图",
);

const thickness = payload["参数"];
addChart(
  "09_厚度结果柱状图.xlsx",
  "比较两个单角度结果、主结果平均值和联合验证值",
  "柱状图",
  [
    ["厚度结果-X", "厚度(微米)-Y"],
    ["10度单角度", thickness["10度厚度_微米"]],
    ["15度单角度", thickness["15度厚度_微米"]],
    ["单角度平均", thickness["平均厚度_微米"]],
    ["双角度联合验证", thickness["联合验证厚度_微米"]],
  ],
  "09_厚度结果柱状图",
);

const summaryMap = Object.fromEntries(payload["汇总"].map((row) => [row["结果类型"], row]));
const metricSpecs = [
  ["RMSE", "RMSE", "10_拟合RMSE柱状图.xlsx", "10_拟合RMSE柱状图", "RMSE", "柱状图"],
  ["MAPE(%)", "MAPE(%)", "11_拟合MAPE柱状图.xlsx", "11_拟合MAPE柱状图", "MAPE百分比", "柱状图"],
  ["R2", "R²", "12_拟合R2柱状图.xlsx", "12_拟合R2柱状图", "R²", "柱状图"],
];
for (const [key, header, fileName, sheetName, description, type] of metricSpecs) {
  addChart(
    fileName,
    `比较10度、15度和联合验证的${description}`,
    type,
    [
      ["拟合对象-X", `${header}-Y`],
      ["10度单角度", summaryMap["10度单角度拟合"][key]],
      ["15度单角度", summaryMap["15度单角度拟合"][key]],
      ["双角度联合验证", summaryMap["双角度共享参数联合拟合"][key]],
    ],
    sheetName,
  );
}

const stability = payload["多初值稳定性表"].slice(1);
function pairRows(label) {
  return stability.filter((row) => row[0] === label).map((row) => [row[2], row[3]]);
}
const s10 = pairRows("10度单角度");
const s15 = pairRows("15度单角度");
const sj = pairRows("双角度联合验证");
const maxRows = Math.max(s10.length, s15.length, sj.length);
addChart(
  "13_多初值稳定性散点.xlsx",
  "用厚度-RMSE散点观察不同初值是否落入不同局部盆地",
  "散点图",
  [
    ["10度厚度-X", "10度RMSE-Y", "15度厚度-X2", "15度RMSE-Y2", "联合厚度-X3", "联合RMSE-Y3"],
    ...Array.from({ length: maxRows }, (_, i) => [
      s10[i]?.[0] ?? null,
      s10[i]?.[1] ?? null,
      s15[i]?.[0] ?? null,
      s15[i]?.[1] ?? null,
      sj[i]?.[0] ?? null,
      sj[i]?.[1] ?? null,
    ]),
  ],
  "13_多初值稳定性散点",
);

const c10 = ecdf(e10);
const c15 = ecdf(e15);
addChart(
  "14_残差ECDF.xlsx",
  "比较两个角度残差绝对规模和累计比例，避免只看均值",
  "经验累计分布图",
  [
    ["10度残差-X", "10度累计比例-Y", "15度残差-X2", "15度累计比例-Y2"],
    ...Array.from({ length: Math.max(c10.length, c15.length) }, (_, i) => [
      c10[i]?.[0] ?? null,
      c10[i]?.[1] ?? null,
      c15[i]?.[0] ?? null,
      c15[i]?.[1] ?? null,
    ]),
  ],
  "14_残差ECDF",
);

for (const chart of chartFiles) {
  await writeWorkbook(chart.fileName, { [chart.sheetName]: allTables[chart.sheetName] });
}
await writeWorkbook("图表总表.xlsx", {
  "图表索引": [
    ["编号", "文件名", "图形类型", "回答的问题", "Origin列结构"],
    ...chartFiles.map((chart, index) => [index + 1, chart.fileName, chart.originType, chart.description, chart.columns.join("；")]),
  ],
  ...allTables,
});

const report = `# q1-q2 Origin 多元图表设计报告

## 使用范围

本文件夹基于已提交的 Sellmeier-Drude-Fresnel 计算结果生成。每张图一个 XLSX 数据表，列名已经标明 X/Y；“图表总表.xlsx”将所有数据集中到独立工作表中，适合批量导入 Origin。

## 统一样式建议

- 画布按单栏 90 mm 或双栏 180 mm 设计；不在图内放大标题，标题放论文图注。
- 中文宋体，英文和数字 Times New Roman；坐标轴标题 9 pt，刻度和图例 8-8.5 pt。
- 10°统一使用蓝色 #006BEE，15°统一使用紫色 #CB5CD7，联合验证使用灰色 #777777。
- 主模型线宽 1.4 pt，参考线 0.8 pt，散点 3.5-4 pt；只保留浅灰主网格。
- 不使用3D、饼图和彩虹色带；热力图采用以零为中心的蓝-白-红发散色带。

## 图表清单

| 文件 | 图形 | 作用 | Origin操作 |
|---|---|---|---|
${chartFiles.map((chart) => `| ${chart.fileName} | ${chart.originType} | ${chart.description} | ${chart.originType === "热力图" ? "绘图-等高线/热图" : chart.originType === "箱线图" ? "绘图-统计-箱线图" : chart.originType === "直方图" ? "绘图-统计-直方图" : chart.originType === "柱状图" ? "绘图-柱/条/饼-柱状图" : chart.originType === "经验累计分布图" ? "绘图-统计-经验累计分布" : chart.originType === "散点图+参考线" ? "绘图-基本二维-散点图" : chart.originType === "散点图" ? "绘图-基本二维-散点图" : "绘图-基本二维-折线图"} |`).join("\n")}

## 直接套用方法

1. 打开对应 XLSX，确认第一行列名；在 Origin 工作表中把“-X”列指定为 X，把“-Y”列指定为 Y。
2. 按上表的 Origin 操作选择图形。多个 Y 列时，保持同一 X 列并分别设置颜色和符号。
3. 热力图数据是“第一行波数、第一列角度、内部单元格为平均残差”的矩阵式表，导入后直接选择矩阵/等高线热图。
4. 箱线图数据是宽表：第一列为样本序号，后两列分别为10度和15度残差；在 Origin 中选两列 Y 直接生成两个箱体，不要先求均值。
5. 多初值稳定性表包含三组 XY 对：10度、15度和联合验证，分别添加为三组散点。
6. “图表总表.xlsx”适合统一保存到一个 Origin 项目；每个工作表对应一张图，不要把不同图的 X/Y 混在同一工作表。

## 解释边界

- 主厚度结论看“09_厚度结果柱状图.xlsx”的“单角度平均”；联合值只是验证。
- 多初值图中的远离主盆地点应保留，它们用于说明局部最优风险，不要删除以美化图形。
- 残差箱线图、直方图和 ECDF 不能替代拟合优度指标，只用于补充误差分布信息。
- 热力图使用分箱平均残差，原始残差仍保留在“05_绝对残差散点.xlsx”和原有拟合残差表中。

## 结果文件

本文件夹只新增 Origin 可直接导入的 XLSX 和本报告，不生成 CSV，不嵌入位图。
`;
await fs.writeFile(path.join(outputDir, "图表设计报告.md"), report, "utf8");
await fs.writeFile(path.join(outputDir, "图表索引.json"), JSON.stringify(chartFiles, null, 2), "utf8");
