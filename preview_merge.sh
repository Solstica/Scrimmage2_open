#!/usr/bin/env bash
# 本地全文预览：在 detached worktree 中临时汇总正式模块并编译全文。
# 不创建 preview 汇总分支，不修改 main，不修改任何正式 feature 分支，不 push。
set -u
IFS=$'\n\t'

REMOTE="origin"
BASE_REMOTE="origin/feature/paper-common-final"
PREVIEW_NAME="run02-full-preview"
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
  "origin/feature/toc"
)

say()  { printf '%s\n' "$*"; }
warn() { printf '\n[提示] %s\n' "$*"; }
die()  { printf '\n[停止] %s\n' "$*" >&2; exit 1; }

repo_root() {
  git rev-parse --show-toplevel 2>/dev/null || return 1
}

canonical_dir() {
  local p="$1"
  if [[ -d "$p" ]]; then
    (cd "$p" 2>/dev/null && pwd -P) || printf '%s\n' "$p"
  else
    printf '%s\n' "$p"
  fi
}

preview_worktree() {
  local p base
  while IFS= read -r p; do
    [[ -n "$p" ]] || continue
    base="$(basename "$p")"
    if [[ -f "$p/$PREVIEW_MARKER" || "$base" == "$PREVIEW_NAME" || "$base" == "$PREVIEW_NAME"-* ]]; then
      printf '%s\n' "$p"
      return 0
    fi
  done < <(git worktree list --porcelain | awk '/^worktree / {print substr($0,10)}')
  return 1
}

worktree_is_registered() {
  local target="$1" target_c p
  target_c="$(canonical_dir "$target")"
  while IFS= read -r p; do
    [[ -n "$p" ]] || continue
    [[ "$(canonical_dir "$p")" == "$target_c" ]] && return 0
  done < <(git worktree list --porcelain | awk '/^worktree / {print substr($0,10)}')
  return 1
}

remove_preview_worktree() {
  local wt="$1" cwd_c wt_c
  cwd_c="$(pwd -P 2>/dev/null || pwd)"
  wt_c="$(canonical_dir "$wt")"

  # Windows 下，父 Git Bash 若正位于目标目录，会锁住目录。此时不要尝试半删除。
  case "$cwd_c/" in
    "$wt_c"/*)
      die "当前终端正位于待删除的预览目录：$wt\n请先 cd 到任一正常 worktree，再重新运行 --clean。"
      ;;
  esac

  if git worktree remove --force "$wt"; then
    return 0
  fi

  warn "Git 未能完整删除预览目录。Windows 上通常是 PDF 阅读器、Fork、资源管理器或其他终端仍占用该目录。"
  if ! worktree_is_registered "$wt"; then
    warn "该路径已不在 git worktree 列表中，仅剩普通目录残留。"
    rm -rf -- "$wt" 2>/dev/null || true
    if [[ -e "$wt" ]]; then
      say "请关闭占用该目录或 main.pdf 的程序后，再手工删除：$wt"
    fi
    git worktree prune
    return 0
  fi

  die "预览 worktree 仍处于 Git 注册状态。请关闭占用该目录的程序后，从正常 worktree 重新运行 --clean。"
}

suggest_preview_dir() {
  local root="$1" parent grand
  parent="$(dirname "$root")"
  grand="$(dirname "$parent")"
  if [[ "$(basename "$parent")" == "worktrees" ]]; then
    printf '%s/%s\n' "$parent" "$PREVIEW_NAME"
  elif [[ -d "$parent/worktrees" ]]; then
    printf '%s/worktrees/%s\n' "$parent" "$PREVIEW_NAME"
  elif [[ -d "$grand/worktrees" ]]; then
    printf '%s/worktrees/%s\n' "$grand" "$PREVIEW_NAME"
  else
    printf '%s/%s\n' "$parent" "$PREVIEW_NAME"
  fi
}

open_pdf() {
  local pdf="$1"
  [[ -f "$pdf" ]] || { warn "PDF 尚不存在：$pdf"; return 1; }
  if command -v cygpath >/dev/null 2>&1 && command -v cmd.exe >/dev/null 2>&1; then
    cmd.exe /c start "" "$(cygpath -w "$pdf")" >/dev/null 2>&1 || true
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$pdf" >/dev/null 2>&1 || true
  else
    say "PDF 路径：$pdf"
  fi
}

clean_preview() {
  local wt
  say ""
  say "========== 清理本地全文预览 =========="
  wt="$(preview_worktree || true)"
  if [[ -n "$wt" ]]; then
    say "检测到预览 worktree：$wt"
    remove_preview_worktree "$wt"
  else
    say "没有检测到已注册的全文预览 worktree。"
  fi

  # 兼容旧脚本遗留的本地 preview/full-paper-local 分支。
  if git show-ref --verify --quiet "refs/heads/${LEGACY_PREVIEW_BRANCH}"; then
    git branch -D "$LEGACY_PREVIEW_BRANCH" >/dev/null 2>&1 \
      || die "无法删除旧版临时分支 ${LEGACY_PREVIEW_BRANCH}。请确认没有 worktree 正在使用它。"
    say "已删除旧版临时分支：${LEGACY_PREVIEW_BRANCH}"
  fi

  git worktree prune
  say "清理完成。正式分支和远端仓库均未修改。"
  exit 0
}

owned_prefix_for() {
  case "$1" in
    origin/feature/abstract)           printf '%s\n' 'modules/00_abstract/' ;;
    origin/feature/restatement)        printf '%s\n' 'modules/10_restatement/' ;;
    origin/feature/notion-paper-a)     printf '%s\n' 'modules/11_notation/' ;;
    origin/feature/assumption-paper-a) printf '%s\n' 'modules/12_assumptions/' ;;
    origin/feature/q1update)           printf '%s\n' 'modules/20_q1/' ;;
    origin/feature/q2-paper-a)         printf '%s\n' 'modules/30_q2/' ;;
    origin/feature/q3-paper-a)         printf '%s\n' 'modules/40_q3/' ;;
    origin/feature/evaluation)         printf '%s\n' 'modules/50_evaluation/' ;;
    origin/feature/toc)                printf '%s\n' 'paper/paper_template.tex' ;;
    *)                                 printf '%s\n' '' ;;
  esac
}

is_common_owned_file() {
  case "$1" in
    paper/main.tex|paper/preamble.tex|paper/sections/*|sections/*)
      return 0 ;;
    *)
      return 1 ;;
  esac
}

is_ignorable_preview_file() {
  case "$1" in
    work/archive/*|archive/*|work/*/archive/*|work/*/output/*|work/*/outputs/*|work/*/results/*|work/cache/*|work/tmp/*|output/*|outputs/*|results/*|*.aux|*.log|*.fls|*.fdb_latexmk|*.synctex.gz)
      return 0 ;;
    *)
      return 1 ;;
  esac
}

remove_conflict_from_preview() {
  local wt="$1" file="$2"
  git -C "$wt" rm -f --ignore-unmatch -- "$file" >/dev/null 2>&1 || true
  if git -C "$wt" ls-files -u -- "$file" | grep -q .; then
    git -C "$wt" update-index --force-remove -- "$file" >/dev/null 2>&1 || true
    rm -f "$wt/$file" 2>/dev/null || true
  fi
}

take_side_or_delete() {
  local wt="$1" side="$2" file="$3"
  if git -C "$wt" checkout "--${side}" -- "$file" >/dev/null 2>&1; then
    git -C "$wt" add -- "$file"
    return 0
  fi
  remove_conflict_from_preview "$wt" "$file"
}

resolve_expected_conflicts() {
  local wt="$1" branch="$2" prefix="$3" file unresolved
  unresolved="$(git -C "$wt" diff --name-only --diff-filter=U)"
  [[ -n "$unresolved" ]] || return 0

  say "发现冲突，按模块所有权处理可判断项："
  while IFS= read -r file; do
    [[ -n "$file" ]] || continue
    if is_ignorable_preview_file "$file"; then
      say "  [忽略] $file"
      remove_conflict_from_preview "$wt" "$file"
    elif [[ -n "$prefix" && "$file" == "$prefix"* ]]; then
      say "  [模块] $file -> ${branch}"
      take_side_or_delete "$wt" theirs "$file"
    elif is_common_owned_file "$file"; then
      say "  [公共] $file -> common-final"
      take_side_or_delete "$wt" ours "$file"
    fi
  done <<< "$unresolved"
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
  local wt="$1" src dst
  src="$wt/paper/paper_template.tex"
  dst="$wt/paper/main.tex"
  [[ -f "$src" ]] || die "找不到 $src；请确认 feature/toc 包含模块化全文入口。"
  say "使用 paper/paper_template.tex 生成本次临时 paper/main.tex"
  cp "$src" "$dst" || die "无法生成临时 paper/main.tex。"
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

  say "全文预览生成完成：$pdf"
  if [[ -f "$pdf" ]]; then
    read -r -p "现在打开 PDF？[Y/n] " ans
    [[ "${ans:-Y}" =~ ^[Nn]$ ]] || open_pdf "$pdf"
  fi
}

main() {
  local root old_wt preview_dir stamp branch prefix choice ans
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

  git show-ref --verify --quiet "refs/remotes/${BASE_REMOTE}" \
    || die "找不到基底分支 ${BASE_REMOTE}。"
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

  # 清理旧版脚本遗留的本地汇总分支；新脚本不会再创建它。
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
  say "看完以后，从任一正常 worktree 运行："
  say "  bash <(git show origin/feature/paper-common-final:preview_merge.sh) --clean"
}

main "$@"
