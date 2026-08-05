import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "file:///C:/Users/rog/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const jsonPath = process.argv[2];
const outputDir = process.argv[3];
const previewDir = process.argv[4] || "";
const payload = JSON.parse(await fs.readFile(jsonPath, "utf8"));
await fs.mkdir(outputDir, { recursive: true });
if (previewDir) await fs.mkdir(previewDir, { recursive: true });

function colName(index) {
  let n = index + 1;
  let out = "";
  while (n > 0) {
    const rem = (n - 1) % 26;
    out = String.fromCharCode(65 + rem) + out;
    n = Math.floor((n - 1) / 26);
  }
  return out;
}

function styleSheet(sheet, rowCount, colCount) {
  sheet.showGridLines = false;
  const lastCol = colName(colCount - 1);
  const used = sheet.getRange(`A1:${lastCol}${rowCount}`);
  used.format.font = { name: "Microsoft YaHei", size: 10, color: "#222222" };
  sheet.getRange(`A1:${lastCol}1`).format = {
    fill: "#1F4E78",
    font: { name: "Microsoft YaHei", size: 10, bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
  };
  used.format.borders = { preset: "all", style: "thin", color: "#D9E2F3" };
  sheet.getRange(`A1:${lastCol}1`).format.rowHeight = 34;
  used.format.autofitColumns();
  sheet.getRange(`A1:${lastCol}${rowCount}`).format.wrapText = false;
  sheet.freezePanes.freezeRows(1);
}

async function writeWorkbook(fileName, tables) {
  const wb = Workbook.create();
  const names = Object.keys(tables);
  for (const [index, name] of names.entries()) {
    const rows = tables[name];
    if (!rows || !rows.length) continue;
    const sheet = wb.worksheets.add(name.slice(0, 31) || `数据${index + 1}`);
    sheet.getRangeByIndexes(0, 0, rows.length, rows[0].length).values = rows;
    styleSheet(sheet, rows.length, rows[0].length);
    if (rows.length > 1 && rows[0].length >= 2) {
      sheet.getRange(`B2:B${rows.length}`).format.numberFormat = "0.000000";
    }
  }
  if (previewDir) {
    for (const name of names) {
      const sheet = wb.worksheets.getItem(name.slice(0, 31));
      const preview = await wb.render({ sheetName: sheet.name, range: "A1:H20", scale: 1, format: "png" });
      await fs.writeFile(path.join(previewDir, `${fileName.replace(/\.xlsx$/i, "")}_${name.slice(0, 20)}.png`), new Uint8Array(await preview.arrayBuffer()));
    }
  }
  const xlsx = await SpreadsheetFile.exportXlsx(wb);
  await xlsx.save(path.join(outputDir, fileName));
}

const tables = payload["表格"];
const fileMap = [
  ["图_附件1_10度原始光谱.xlsx", "附件1_10度原始光谱"],
  ["图_附件2_15度原始光谱.xlsx", "附件2_15度原始光谱"],
  ["图_10度实测与模型拟合.xlsx", "10度实测与模型拟合"],
  ["图_15度实测与模型拟合.xlsx", "15度实测与模型拟合"],
  ["图_10度模型拟合残差.xlsx", "10度模型拟合残差"],
  ["图_15度模型拟合残差.xlsx", "15度模型拟合残差"],
];
for (const [fileName, key] of fileMap) await writeWorkbook(fileName, { [key]: tables[key] });

const summaryKeys = [...new Set(payload["汇总"].flatMap((row) => Object.keys(row)))];
const summaryRows = [summaryKeys, ...payload["汇总"].map((row) => summaryKeys.map((key) => row[key] ?? null))];
const parameterRows = payload["模型参数表"] || [["参数", "数值"], ...Object.entries(payload["参数"]).map(([key, value]) => [key, Array.isArray(value) ? value.join(", ") : value])];
const stabilityRows = payload["多初值稳定性表"] || [];
const thicknessRows = [
  ["厚度结果-X", "厚度(微米)-Y"],
  ["10度单角度", payload["参数"]["10度厚度_微米"]],
  ["15度单角度", payload["参数"]["15度厚度_微米"]],
  ["单角度平均", payload["参数"]["平均厚度_微米"]],
  ["双角度联合验证", payload["参数"]["联合验证厚度_微米"]],
];

await writeWorkbook("总表.xlsx", {
  "总表": summaryRows,
  "模型参数": parameterRows,
  "多初值稳定性": stabilityRows,
  "厚度结果对比": thicknessRows,
});
await writeWorkbook("图_双角度厚度对比.xlsx", { "双角度厚度对比": thicknessRows });
await writeWorkbook("结果汇总.xlsx", {
  "总表": summaryRows,
  "模型参数": parameterRows,
  "多初值稳定性": stabilityRows,
  "厚度结果对比": thicknessRows,
  ...tables,
});

await fs.writeFile(
  path.join(outputDir, "run_metadata.json"),
  JSON.stringify(
    {
      模型: "Sellmeier-Drude-Fresnel 双光束；10度、15度单角度拟合取平均；双角度共享参数只作验证",
      相位约定: "exp(-i Delta phi)",
      输入文件: ["附件1 (1).xlsx", "附件2 (1).xlsx"],
      参数: payload["参数"],
    },
    null,
    2,
  ),
  "utf8",
);
