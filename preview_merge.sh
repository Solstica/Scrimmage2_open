#!/usr/bin/env bash
set -u

# 本地全文合并预览：在 detached worktree 中临时汇总正式模块；
# 不创建 preview 汇总分支，不改动正式远端分支。

REMOTE="origin"
BASE_REMOTE="${PREVIEW_BASE_REF:-origin/feature/paper-common-final}"
PREVIEW_MARKER=".full-paper-preview"
LEGACY_PREVIEW_BRANCH="preview/full-paper-local"

MERGE_BRANCHES=(
  "origin/feature/abstract"
  "origin/feature/restatement"
  "origin/feature/notion-paper-a"
  "origin/feature/assumption-paper-a"
  "origin/feature/q1update"
  "origin/feature/q2-paper-a"
  "origin/feature/q3-paper-a"
  "origin/feature/evaluation"
  "origin/feature/appendix-code"
)

say() { printf '%s\n' "$*"; }
warn() { printf '[警告] %s\n' "$*" >&2; }
die() { printf '\n[停止] %s\n' "$*" >&2; exit 1; }

repo_root() {
  git rev-parse --show-toplevel 2>/dev/null
}

normalize_path() {
  local p="$1"
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -am "$p" 2>/dev/null || printf '%s\n' "$p"
  else
    printf '%s\n' "$p"
  fi
}

preview_worktree() {
  local wt marker
  while IFS= read -r wt; do
    [[ -z "$wt" ]] && continue
    marker="$wt/$PREVIEW_MARKER"
    if [[ -f "$marker" ]]; then
      printf '%s\n' "$wt"
      return 0
    fi
  done < <(git worktree list --porcelain | awk '/^worktree /{sub(/^worktree /,""); print}')
  return 1
}

suggest_preview_dir() {
  local root="$1" parent base
  parent="$(dirname "$root")"
  base="$(basename "$root")"
  if [[ "$base" == run02-* ]]; then
    printf '%s\n' "$parent/run02-full-preview"
  else
    printf '%s\n' "$parent/full-paper-preview"
  fi
}

safe_cd_outside() {
  local doomed="$1" wt
  if [[ "$(normalize_path "$PWD")" == "$(normalize_path "$doomed")"* ]]; then
    while IFS= read -r wt; do
      [[ -z "$wt" ]] && continue
      if [[ "$(normalize_path "$wt")" != "$(normalize_path "$doomed")" ]]; then
        cd "$wt" 2>/dev/null && return 0
      fi
    done < <(git worktree list --porcelain | awk '/^worktree /{sub(/^worktree /,""); print}')
    cd "$(dirname "$doomed")" 2>/dev/null || true
  fi
}

remove_preview_worktree() {
  local wt="$1"
  safe_cd_outside "$wt"
  git worktree remove --force "$wt" 2>/dev/null || {
    git worktree prune 2>/dev/null || true
    if [[ -e "$wt" ]]; then
      rm -rf "$wt" 2>/dev/null || die "无法删除临时预览目录 $wt。请关闭PDF、Fork标签页、资源管理器和停在该目录中的终端后重试。"
    fi
  }
  git worktree prune 2>/dev/null || true
}

clean_preview() {
  local root wt
  root="$(repo_root)" || die "当前目录不是有效 Git worktree。请先 cd 到任一正常 worktree 后运行。"
  wt="$(preview_worktree || true)"
  if [[ -n "$wt" ]]; then
    say "========== 清理本地全文预览 =========="
    say "检测到预览 worktree：$wt"
    remove_preview_worktree "$wt"
    say "已删除临时预览 worktree。"
  fi
  if git show-ref --verify --quiet "refs/heads/${LEGACY_PREVIEW_BRANCH}"; then
    git branch -D "$LEGACY_PREVIEW_BRANCH" >/dev/null 2>&1 || true
    say "已清理旧版临时分支 ${LEGACY_PREVIEW_BRANCH}。"
  fi
  git worktree prune 2>/dev/null || true
  exit 0
}

open_pdf() {
  local pdf="$1"
  [[ -f "$pdf" ]] || return 0
  if command -v start >/dev/null 2>&1; then
    start "" "$pdf" >/dev/null 2>&1 || true
  elif command -v cmd.exe >/dev/null 2>&1; then
    cmd.exe /c start "" "$(cygpath -w "$pdf" 2>/dev/null || printf '%s' "$pdf")" >/dev/null 2>&1 || true
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$pdf" >/dev/null 2>&1 || true
  fi
}

owned_prefix_for() {
  case "$1" in
    origin/feature/abstract) printf '%s\n' 'modules/00_abstract/' ;;
    origin/feature/restatement) printf '%s\n' 'modules/10_restatement/' ;;
    origin/feature/notion-paper-a) printf '%s\n' 'modules/11_notation/' ;;
    origin/feature/assumption-paper-a) printf '%s\n' 'modules/12_assumptions/' ;;
    origin/feature/q1update) printf '%s\n' 'modules/20_q1/' ;;
    origin/feature/q2-paper-a) printf '%s\n' 'modules/30_q2/' ;;
    origin/feature/q3-paper-a) printf '%s\n' 'modules/40_q3/' ;;
    origin/feature/evaluation) printf '%s\n' 'modules/50_evaluation/' ;;
    origin/feature/appendix-code) printf '%s\n' 'modules/70_appendix/' ;;
    *) printf '%s\n' '' ;;
  esac
}

is_common_owned() {
  case "$1" in
    paper/preamble.tex|paper/preamble_simple.tex|paper/main.tex|paper/paper_template.tex|paper/abstract_check.tex|paper/training_toc.tex|preview_merge.sh) return 0 ;;
    modules/60_references/*|modules/80_ai_report/*) return 0 ;;
    scripts/*|work/*|docs/team_handoff/*) return 0 ;;
    *) return 1 ;;
  esac
}

is_module_owned() {
  local path="$1" prefix="$2"
  [[ -n "$prefix" && "$path" == "$prefix"* ]]
}

take_side_or_delete() {
  local wt="$1" side="$2" path="$3"
  if git -C "$wt" checkout "--$side" -- "$path" 2>/dev/null; then
    git -C "$wt" add -- "$path"
  else
    git -C "$wt" rm -f --ignore-unmatch -- "$path" >/dev/null 2>&1 || true
    git -C "$wt" add -A -- "$path" >/dev/null 2>&1 || true
  fi
}

resolve_expected_conflicts() {
  local wt="$1" branch="$2" prefix="$3" conflicts f unresolved=()
  conflicts="$(git -C "$wt" diff --name-only --diff-filter=U)"
  [[ -z "$conflicts" ]] && return 0

  say "发现冲突，按模块所有权处理可判断项："
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    if is_module_owned "$f" "$prefix"; then
      say "  [模块] $f -> $branch"
      take_side_or_delete "$wt" theirs "$f"
    elif is_common_owned "$f"; then
      say "  [公共] $f -> common-final"
      take_side_or_delete "$wt" ours "$f"
    elif [[ "$f" == work/archive/* || "$f" == output/* || "$f" == modules/paper汇总/* ]]; then
      say "  [忽略] $f -> common-final/当前汇总"
      take_side_or_delete "$wt" ours "$f"
    else
      unresolved+=("$f")
    fi
  done <<< "$conflicts"

  if [[ ${#unresolved[@]} -gt 0 ]]; then
    say "仍有无法自动判断的冲突："
    printf '  - %s\n' "${unresolved[@]}"
    return 1
  fi
  return 0
}

finish_merge_interactively() {
  local wt="$1" branch="$2" remaining choice f
  while true; do
    remaining="$(git -C "$wt" diff --name-only --diff-filter=U)"
    if [[ -z "$remaining" ]]; then
      git -C "$wt" commit --no-edit >/dev/null 2>&1 \
        || die "冲突已解决，但临时 merge commit 创建失败。"
      return 0
    fi

    say "仍有无法自动判断的冲突："
    while IFS= read -r f; do [[ -n "$f" ]] && say "  - $f"; done <<< "$remaining"
    say "  1) 安全停止"
    say "  2) 全部保留 common-final"
    say "  3) 全部采用当前模块分支"
    say "  4) 手工解决后继续"
    read -r -p "输入 1/2/3/4 [默认 1]：" choice
    choice="${choice:-1}"
    case "$choice" in
      1)
        git -C "$wt" merge --abort || true
        die "已停止 ${branch} 的临时合并。预览目录保留在：$wt"
        ;;
      2)
        while IFS= read -r f; do [[ -n "$f" ]] && take_side_or_delete "$wt" ours "$f"; done <<< "$remaining"
        ;;
      3)
        while IFS= read -r f; do [[ -n "$f" ]] && take_side_or_delete "$wt" theirs "$f"; done <<< "$remaining"
        ;;
      4)
        say "仅在临时目录中解决冲突：$wt"
        read -r -p "完成 git add 后按 Enter 继续检查... " _
        ;;
      *) say "输入无效。" ;;
    esac
  done
}

materialize_modular_entry() {
  local wt="$1" src dst assumptions_src assumptions_dst
  src="$wt/paper/paper_template.tex"
  dst="$wt/paper/main.tex"
  [[ -f "$src" ]] || die "找不到 $src；请确认公共论文分支包含模块化全文入口。"
  say "使用 paper/paper_template.tex 生成本次临时 paper/main.tex"
  cp "$src" "$dst" || die "无法生成临时 paper/main.tex。"
  # 稳定门禁按 paper/sections/02_assumptions.tex 统计 \item；预览时将
  # 模块源临时物化到该路径，避免把模块化 \input 误判为“0 条假设”。
  assumptions_src="$wt/modules/12_assumptions/paper/assumptions.tex"
  assumptions_dst="$wt/paper/sections/02_assumptions.tex"
  [[ -f "$assumptions_src" ]] || die "找不到 $assumptions_src。"
  cp "$assumptions_src" "$assumptions_dst" || die "无法物化模型假设门禁输入。"
}

run_final_preflight() {
  local wt="$1"
  local conda_base phasefield_py
  local -a py_cmd=()
  conda_base=""
  if command -v conda >/dev/null 2>&1; then
    conda_base="$(conda info --base 2>/dev/null || true)"
  fi
  phasefield_py="${conda_base}/envs/phasefield/python.exe"
  if [[ -n "$conda_base" && -x "$phasefield_py" ]]; then
    py_cmd=("$phasefield_py")
  elif command -v conda >/dev/null 2>&1 \
    && conda run -n phasefield python -c "import sys" >/dev/null 2>&1; then
    py_cmd=(conda run -n phasefield python)
  elif command -v python >/dev/null 2>&1; then
    py_cmd=(python)
  elif command -v python3 >/dev/null 2>&1; then
    py_cmd=(python3)
  else
    warn "未检测到Python，跳过终稿preflight。"
    return 0
  fi
  [[ -f "$wt/scripts/final_preflight.py" ]] || { warn "未找到 scripts/final_preflight.py，跳过终稿preflight。"; return 0; }
  say ""
  say "========== 终稿 Preflight =========="
  if ! (cd "$wt" && "${py_cmd[@]}" scripts/final_preflight.py --post-build); then
    warn "终稿preflight发现FAIL项。PDF仍保留，请按输出逐项处理后再提交。"
  fi
}

compile_paper() {
  local wt="$1" paper_dir pdf ans
  paper_dir="$wt/paper"
  pdf="$paper_dir/main.pdf"
  [[ -f "$paper_dir/main.tex" ]] || die "找不到 $paper_dir/main.tex。"

  say ""
  say "========== 编译 paper/main.tex =========="
  if command -v latexmk >/dev/null 2>&1; then
    (cd "$paper_dir" && latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex) \
      || die "LaTeX 编译失败。日志：$paper_dir/main.log"
  elif command -v xelatex >/dev/null 2>&1; then
    (cd "$paper_dir" && xelatex -interaction=nonstopmode -halt-on-error main.tex && xelatex -interaction=nonstopmode -halt-on-error main.tex) \
      || die "LaTeX 编译失败。日志：$paper_dir/main.log"
  else
    warn "未检测到 latexmk/xelatex。临时汇总已完成，但无法自动编译。"
    return 0
  fi

  run_final_preflight "$wt"

  say "全文预览生成完成：$pdf"
  if [[ -f "$pdf" ]]; then
    read -r -p "现在打开 PDF？[Y/n] " ans
    [[ "${ans:-Y}" =~ ^[Nn]$ ]] || open_pdf "$pdf"
  fi
}

main() {
  local root old_wt preview_dir stamp branch prefix choice
  root="$(repo_root)" || die "当前目录不是有效 Git worktree。请先 cd 到任一正常 worktree 后运行。"
  cd "$root" || die "无法进入仓库根目录。"

  if [[ "${1:-}" == "--clean" ]]; then
    clean_preview
  fi

  if [[ -f "$root/$PREVIEW_MARKER" ]]; then
    die "你现在位于临时全文预览 worktree。请回到任一正常 worktree 后重新运行。"
  fi

  say "========== 本地全文 Merge 预览 =========="
  say "当前工作目录：$root"
  say "本次预览使用 detached HEAD，不创建任何本地汇总分支。"

  say "[1/6] 获取远端最新状态..."
  git fetch "$REMOTE" --prune || die "git fetch 失败。"

  git rev-parse --verify --quiet "${BASE_REMOTE}^{commit}" >/dev/null \
    || die "找不到基底引用 ${BASE_REMOTE}。"
  for branch in "${MERGE_BRANCHES[@]}"; do
    git show-ref --verify --quiet "refs/remotes/${branch}" \
      || die "找不到远端分支 ${branch}。"
  done

  old_wt="$(preview_worktree || true)"
  if [[ -n "$old_wt" ]]; then
    say "检测到上一次全文预览：$old_wt"
    say "  1) 删除旧预览并重新生成（推荐）"
    say "  2) 直接打开旧 PDF"
    say "  3) 退出"
    read -r -p "输入 1/2/3 [默认 1]：" choice
    choice="${choice:-1}"
    case "$choice" in
      1) remove_preview_worktree "$old_wt" ;;
      2) open_pdf "$old_wt/paper/main.pdf"; exit 0 ;;
      *) exit 0 ;;
    esac
  fi

  if git show-ref --verify --quiet "refs/heads/${LEGACY_PREVIEW_BRANCH}"; then
    git branch -D "$LEGACY_PREVIEW_BRANCH" >/dev/null 2>&1 \
      || die "旧版临时分支 ${LEGACY_PREVIEW_BRANCH} 仍被某个 worktree 使用，请先清理旧预览。"
  fi

  preview_dir="$(suggest_preview_dir "$root")"
  if [[ -e "$preview_dir" ]]; then
    stamp="$(date +%Y%m%d-%H%M%S)"
    preview_dir="${preview_dir}-${stamp}"
    warn "默认预览目录已有普通残留，改用：$preview_dir"
  fi

  say "[2/6] 创建 detached 临时 worktree..."
  git worktree add --detach "$preview_dir" "$BASE_REMOTE" \
    || die "创建预览 worktree 失败。"
  : > "$preview_dir/$PREVIEW_MARKER"

  say "[3/6] 依次临时合并正式模块分支..."
  for branch in "${MERGE_BRANCHES[@]}"; do
    say "---- $branch ----"
    if git -C "$preview_dir" merge --no-ff --no-edit "$branch"; then
      continue
    fi
    if [[ -z "$(git -C "$preview_dir" diff --name-only --diff-filter=U)" ]]; then
      die "合并 ${branch} 失败，但没有检测到普通文本冲突。"
    fi
    prefix="$(owned_prefix_for "$branch")"
    resolve_expected_conflicts "$preview_dir" "$branch" "$prefix"
    finish_merge_interactively "$preview_dir" "$branch"
  done

  say "[4/6] 生成模块化全文入口..."
  materialize_modular_entry "$preview_dir"

  say "[5/6] 检查临时汇总状态..."
  git -C "$preview_dir" status --short || true

  say "[6/6] 编译全文..."
  compile_paper "$preview_dir"

  say ""
  say "临时预览 worktree：$preview_dir"
  say "该 worktree 为 detached HEAD，没有 preview/full-paper-local 分支。"
  say "看完以后，从任一正常 worktree运行："
  say "  bash <(git show origin/feature/paper-common-final:preview_merge.sh) --clean"
}

main "$@"
