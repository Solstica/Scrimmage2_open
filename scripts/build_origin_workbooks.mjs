import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";


const project = path.resolve(process.argv[2]);
const deliverables = path.resolve(process.argv[3]);
const previewRoot = path.resolve(process.argv[4]);

const configs = [
  {
    key: "q2",
    title: "Q2 PAPER_A Origin data",
    route: "Independent 10deg and 15deg fits followed by arithmetic mean",
    frozen: "10deg 7.8566 um; 15deg 7.6230 um; mean 7.7398 um",
    base: "modules/30_q2/figures/editable/origin_data",
    files: [
      "q2_raw_10deg.csv", "q2_raw_15deg.csv",
      "q2_fit_10deg.csv", "q2_fit_15deg.csv", "q2_summary.csv",
      "q2_multistart.csv", "q2_residual_histogram.csv",
      "q2_residual_boxplot.csv", "q2_residual_heatmap.csv",
      "q2_residual_ecdf.csv", "q2_basin_stage1.csv",
      "q2_basin_refined.csv", "q2_basin_summary.csv",
    ],
  },
  {
    key: "q3",
    title: "Q3 PAPER_A Origin data",
    route: "Airy is formal; double beam appears only at the same frozen parameters",
    frozen: "10deg 3.2480 um; 15deg 3.1875 um; mean 3.2178 um",
    base: "modules/40_q3/figures/editable/origin_data",
    files: [
      "q3_fit_10deg.csv", "q3_fit_15deg.csv", "q3_summary.csv",
      "q3_multistart.csv", "q3_sic_backcheck.csv",
      "q3_residual_boxplot.csv", "q3_residual_heatmap.csv",
      "q3_thickness.csv", "q3_identifiability.csv",
      "q3_threshold_context.csv", "q3_validation_comparison.csv",
      "q3_identifiability_summary_detailed.csv",
      "q3_identifiability_parameters.csv",
      "q3_identifiability_correlation.csv",
      "q3_multistart_diagnostics.csv",
      "q3_extended_jacobian_summary.csv",
      "q3_extended_jacobian_parameters.csv",
    ],
  },
];


function columnName(number) {
  let value = number;
  let output = "";
  while (value > 0) {
    value -= 1;
    output = String.fromCharCode(65 + (value % 26)) + output;
    value = Math.floor(value / 26);
  }
  return output;
}


function sheetName(filename) {
  return path.basename(filename, ".csv").slice(0, 31);
}


function numberFormat(header) {
  const name = String(header).toLowerCase();
  if (name.includes("wavenumber") || name.includes("cm1")) return "0.000";
  if (name.includes("angle_deg")) return "0.0";
  if (name.includes("count") || name.includes("rank") || name.includes("seed_id") || name.includes("sample_id")) return "0";
  if (name.includes("success") || name.includes("defined") || name.includes("fit_band")) return "0";
  if (name.includes("thickness") || name.includes("d_init") || name.includes("d_final")) return "0.000000";
  if (name.includes("reflectance") || name.includes("residual") || name.includes("rmse") || name === "r2") return "0.000000E+00";
  if (name.includes("percent") || name.includes("fraction") || name.includes("ratio") || name.includes("ecdf")) return "0.000000E+00";
  if (name.includes("jacobian") || name.includes("condition") || name.includes("sensitivity") || name.includes("singular") || name.includes("sigma") || name.includes("log10") || name.includes("n3")) return "0.000000E+00";
  return "General";
}


function coerceValues(values) {
  return values.map((row, rowIndex) => row.map((value) => {
    if (rowIndex === 0) return String(value ?? "").replace(/^\uFEFF/, "");
    if (value === null || value === undefined || value === "") return null;
    if (value === "True") return true;
    if (value === "False") return false;
    if (typeof value === "string" && /^[+-]?(?:\d+\.?\d*|\.\d+)(?:[Ee][+-]?\d+)?$/.test(value.trim())) {
      return Number(value);
    }
    return value;
  }));
}


async function addCsvSheet(workbook, csvPath) {
  const csvText = (await fs.readFile(csvPath, "utf8")).replace(/^\uFEFF/, "");
  const name = sheetName(csvPath);
  const imported = await Workbook.fromCSV(csvText, { sheetName: name });
  const importedSheet = imported.worksheets.getItem(name);
  const values = coerceValues(importedSheet.getUsedRange(true).values);
  const rows = values.length;
  const cols = values[0]?.length ?? 1;
  const sheet = workbook.worksheets.add(name);
  sheet.getRangeByIndexes(0, 0, rows, cols).values = values;
  const used = sheet.getUsedRange(true);
  const header = sheet.getRangeByIndexes(0, 0, 1, cols);

  sheet.showGridLines = false;
  sheet.freezePanes.freezeRows(1);
  used.format = {
    font: { typeface: "Microsoft YaHei", fontSize: 10, color: "#222222" },
    borders: { preset: "all", style: "thin", color: "#D9E2F3" },
  };
  header.format = {
    fill: "#1F4E78",
    font: { typeface: "Microsoft YaHei", fontSize: 10, bold: true, color: "#FFFFFF" },
    borders: { preset: "all", style: "thin", color: "#D9E2F3" },
    horizontalAlignment: "center",
    wrapText: true,
    rowHeight: 30,
  };

  for (let col = 0; col < cols; col += 1) {
    const label = values[0][col];
    const range = sheet.getRangeByIndexes(1, col, Math.max(rows - 1, 1), 1);
    const format = numberFormat(label);
    if (format !== "General") range.setNumberFormat(format);
    let width = Math.min(28, Math.max(12, String(label).length + 3));
    if (String(label).includes("boundary_hits")) width = 60;
    if (["parameter", "parameter_i", "parameter_j"].includes(String(label))) width = 28;
    if (["result_type", "usage", "role", "metric"].includes(String(label))) width = 30;
    sheet.getRangeByIndexes(0, col, rows, 1).format.columnWidth = width;
  }
  return { sheet, rows, cols };
}


async function buildWorkbook(config) {
  const workbook = Workbook.create();
  const readme = workbook.worksheets.add("README");
  readme.showGridLines = false;
  readme.getRange("A1:B7").values = [
    ["Field", "Value"],
    ["Dataset", config.title],
    ["Formal route", config.route],
    ["Frozen results", config.frozen],
    ["Workbook role", "Origin import data; no embedded bitmap charts"],
    ["CSV source", `${config.base.replaceAll("\\", "/")}/csv/`],
    ["Regeneration", "Run Q2/Q3 solvers, export_origin_data.py, then build_origin_workbooks.mjs"],
  ];
  readme.getRange("A1:B7").format = {
    font: { typeface: "Microsoft YaHei", fontSize: 10, color: "#222222" },
    borders: { preset: "all", style: "thin", color: "#D9E2F3" },
  };
  readme.getRange("A1:B1").format = {
    fill: "#1F4E78",
    font: { typeface: "Microsoft YaHei", fontSize: 10, bold: true, color: "#FFFFFF" },
    borders: { preset: "all", style: "thin", color: "#D9E2F3" },
  };
  readme.getRange("A1:A7").format.columnWidth = 22;
  readme.getRange("B1:B7").format.columnWidth = 80;
  readme.getRange("B2:B7").format.wrapText = true;
  readme.freezePanes.freezeRows(1);

  const sheetInfo = [{ sheet: readme, rows: 7, cols: 2 }];
  for (const filename of config.files) {
    const csvPath = path.join(project, config.base, "csv", filename);
    sheetInfo.push(await addCsvSheet(workbook, csvPath));
  }

  const previewDir = path.join(previewRoot, config.key);
  await fs.mkdir(previewDir, { recursive: true });
  for (const info of sheetInfo) {
    const lastColumn = columnName(info.cols);
    const lastRow = Math.min(info.rows, 20);
    const preview = await workbook.render({
      sheetName: info.sheet.name,
      range: `A1:${lastColumn}${lastRow}`,
      scale: 1.4,
      format: "png",
    });
    await fs.writeFile(
      path.join(previewDir, `${info.sheet.name}.png`),
      new Uint8Array(await preview.arrayBuffer()),
    );
  }

  const keySheet = config.key === "q2" ? "q2_summary" : "q3_summary";
  const check = await workbook.inspect({
    kind: "table",
    range: `${keySheet}!A1:L8`,
    include: "values,formulas",
    tableMaxRows: 8,
    tableMaxCols: 12,
    maxChars: 4000,
  });
  process.stdout.write(`${check.ndjson}\n`);
  const errors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 100 },
    summary: `${config.key} formula error scan`,
    maxChars: 2000,
  });
  process.stdout.write(`${errors.ndjson}\n`);

  const repoOutput = path.join(project, config.base, `${config.key}_origin_data.xlsx`);
  const userOutput = path.join(deliverables, `${config.key}_origin_data.xlsx`);
  await fs.mkdir(path.dirname(repoOutput), { recursive: true });
  await fs.mkdir(deliverables, { recursive: true });
  const blob = await SpreadsheetFile.exportXlsx(workbook);
  await blob.save(repoOutput);
  await blob.save(userOutput);
}


for (const config of configs) {
  await buildWorkbook(config);
}
