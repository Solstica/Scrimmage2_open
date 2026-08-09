#!/usr/bin/env bash
# 本地全文预览：把各正式模块分支临时合到一个 disposable worktree 中并编译 paper/main.tex。
# 不修改 main，不修改任何正式 feature 分支，不 push。
set -u
IFS=$'\n\t'

REMOTE="origin"
BASE_REMOTE="origin/feature/paper-common-final"
PREVIEW_BRANCH="preview/full-paper-local"
PREVIEW_NAME="run02-full-preview"

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

preview_worktree_for_branch() {
  git worktree list --porcelain | awk -v ref="refs/heads/${PREVIEW_BRANCH}" '
    /^worktree / { p=substr($0,10) }
    /^branch /   { b=substr($0,8); if (b==ref) { print p; exit } }
  '
}

safe_worktree_for_cleanup() {
  local target="$1" target_c p p_c
  target_c="$(canonical_dir "$target")"
  while IFS= read -r p; do
    [[ -n "$p" ]] || continue
    p_c="$(canonical_dir "$p")"
    [[ "$p_c" == "$target_c" ]] && continue
    if git -C "$p" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      printf '%s\n' "$p"
      return 0
    fi
  done < <(git worktree list --porcelain | awk '/^worktree / {print substr($0,10)}')
  return 1
}

worktree_is_registered() {
  local target="$1" target_c p p_c
  target_c="$(canonical_dir "$target")"
  while IFS= read -r p; do
    [[ -n "$p" ]] || continue
    p_c="$(canonical_dir "$p")"
    [[ "$p_c" == "$target_c" ]] && return 0
  done < <(git worktree list --porcelain | awk '/^worktree / {print substr($0,10)}')
  return 1
}

remove_preview_worktree_safely() {
  local wt="$1" cwd_c wt_c safe
  cwd_c="$(pwd -P 2>/dev/null || pwd)"
  wt_c="$(canonical_dir "$wt")"

  # Windows 不能删除当前 shell 正在占用的目录。若人在预览 worktree 内，先切到其他正常 worktree。
  case "$cwd_c/" in
    "$wt_c"/*)
      safe="$(safe_worktree_for_cleanup "$wt" || true)"
      [[ -n "$safe" ]] || die "当前 shell 位于待删除的预览 worktree 中，且没有找到其他可用 worktree。请先 cd 到任一正常 worktree 后重试。"
      say "当前 shell 位于待删除目录内，先切换到安全 worktree：$safe"
      cd "$safe" || die "无法切换到安全 worktree：$safe"
      ;;
  esac

  if git worktree remove --force "$wt"; then
    return 0
  fi

  warn "Git 未能完整删除预览目录。Windows 上通常是 PDF 阅读器、Fork、资源管理器或终端仍占用该目录。"

  # 某些 Git for Windows 版本会先解除 worktree 注册，再因文件占用导致目录删除失败。
  # 这种情况下只清理已经失去 Git 注册的普通残留目录，不触碰任何有效 worktree 的 .git 元数据。
  if ! worktree_is_registered "$wt"; then
    warn "该路径已经不在 git worktree 列表中，仅剩普通目录残留。尝试删除残留目录。"
    rm -rf -- "$wt" 2>/dev/null || true
    if [[ -e "$wt" ]]; then
      warn "目录仍被 Windows 占用：$wt"
      say "请关闭打开该目录/PDF的 Fork 标签页、文件资源管理器和阅读器后，再手工删除这个普通残留目录。"
    fi
    git worktree prune
    return 0
  fi

  die "预览 worktree 仍处于 Git 注册状态，暂不做破坏性处理。请关闭占用该目录的程序后，从正常 worktree 重新运行 --clean。"
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
  wt="$(preview_worktree_for_branch || true)"
  say ""
  say "========== 清理本地全文预览 =========="
  if [[ -n "$wt" ]]; then
    say "检测到预览 worktree：$wt"
    if [[ -n "$(git -C "$wt" status --porcelain 2>/dev/null || true)" ]]; then
      warn "预览目录内存在未提交改动/未完成合并。该目录是一次性的，可以直接丢弃。"
      read -r -p "删除这个临时预览并丢弃其中改动？[Y/n] " ans
      [[ ! "${ans:-Y}" =~ ^[Nn]$ ]] || { say "已取消。"; exit 0; }
    fi
    remove_preview_worktree_safely "$wt"
  else
    say "没有检测到 ${PREVIEW_BRANCH} 对应的已注册 worktree。"
  fi

  if git show-ref --verify --quiet "refs/heads/${PREVIEW_BRANCH}"; then
    git branch -D "$PREVIEW_BRANCH" || die "临时 branch 删除失败。"
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

# 这些都是历史归档、运行输出或缓存，不参与当前论文正文。
# 在一次性全文预览中若发生冲突，直接从预览树删除，不再询问用户。
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

# 对普通“删除/修改”冲突也做容错：若某一侧根本没有该文件，则该侧的含义就是删除。
take_side_or_delete() {
  local wt="$1" side="$2" file="$3"
  if git -C "$wt" checkout "--${side}" -- "$file" >/dev/null 2>&1; then
    git -C "$wt" add -- "$file"
    return 0
  fi

  warn "$file 在 ${side} 一侧不存在（典型删除/修改冲突），按该侧的‘删除’处理。"
  remove_conflict_from_preview "$wt" "$file"
}

resolve_expected_conflicts() {
  local wt="$1" branch="$2" prefix="$3" file unresolved
  unresolved="$(git -C "$wt" diff --name-only --diff-filter=U)"
  [[ -n "$unresolved" ]] || return 0

  say ""
  say "发现冲突，先按项目约定自动处理可判断项："
  say "  - work/archive、output、results 等历史/运行文件：预览中直接忽略"
  say "  - 当前模块目录 ${prefix:-<未知>}：采用待合入分支版本"
  say "  - paper/main.tex / preamble / sections：采用 common-final 版本"

  while IFS= read -r file; do
    [[ -n "$file" ]] || continue
    if is_ignorable_preview_file "$file"; then
      say "  [忽略] $file -> 与论文正文无关，从临时预览删除"
      remove_conflict_from_preview "$wt" "$file"
    elif [[ -n "$prefix" && "$file" == "$prefix"* ]]; then
      say "  [模块] $file -> 采用 ${branch}"
      take_side_or_delete "$wt" theirs "$file"
    elif is_common_owned_file "$file"; then
      say "  [公共] $file -> 保留 common-final"
      take_side_or_delete "$wt" ours "$file"
    fi
  done <<< "$unresolved"
}

finish_merge_interactively() {
  local wt="$1" branch="$2" remaining choice f
  while true; do
    remaining="$(git -C "$wt" diff --name-only --diff-filter=U)"
    if [[ -z "$remaining" ]]; then
      git -C "$wt" commit --no-edit >/dev/null 2>&1 || die "冲突已解决，但 merge commit 创建失败。"
      say "冲突已自动解决并完成合并。"
      return 0
    fi

    say ""
    say "仍有脚本无法安全判断的冲突文件："
    while IFS= read -r f; do
      [[ -n "$f" ]] && say "  - $f"
    done <<< "$remaining"
    say ""
    say "请选择："
    say "  1) 安全停止（推荐：不碰正式分支，保留预览目录供管理员处理）"
    say "  2) 剩余冲突全部保留 common-final 版本"
    say "  3) 剩余冲突全部采用当前待合入分支版本"
    say "  4) 我自己手工解决；解决完后回这里继续检查"
    read -r -p "输入 1/2/3/4 [默认 1]：" choice
    choice="${choice:-1}"

    case "$choice" in
      1)
        git -C "$wt" merge --abort || true
        warn "已取消当前分支 ${branch} 的合并并停止。"
        say "预览目录仍保留在：$wt"
        say "把上面的冲突文件名发给管理员即可。"
        exit 2
        ;;
      2)
        while IFS= read -r f; do
          [[ -n "$f" ]] || continue
          take_side_or_delete "$wt" ours "$f"
        done <<< "$remaining"
        ;;
      3)
        while IFS= read -r f; do
          [[ -n "$f" ]] || continue
          take_side_or_delete "$wt" theirs "$f"
        done <<< "$remaining"
        ;;
      4)
        say ""
        say "请只在这个临时目录解决冲突："
        say "  $wt"
        say "解决后执行 git add <已解决文件>，然后回到这个窗口按 Enter。"
        read -r -p "按 Enter 重新检查... " _
        ;;
      *)
        say "输入无效。"
        ;;
    esac
  done
}

materialize_modular_entry() {
  local wt="$1" src dst
  src="$wt/paper/paper_template.tex"
  dst="$wt/paper/main.tex"

  [[ -f "$src" ]] || die "找不到 $src；请确认 feature/toc 已包含模块化全文入口。"
  say ""
  say "========== 生成本次预览的模块化全文入口 =========="
  say "使用：paper/paper_template.tex -> paper/main.tex"
  cp "$src" "$dst" || die "无法生成临时 paper/main.tex。"
  git -C "$wt" add paper/main.tex
  if ! git -C "$wt" diff --cached --quiet; then
    git -C "$wt" commit -m "preview: materialize modular paper entry" >/dev/null 2>&1 \
      || die "临时全文入口提交失败。"
  fi
}

compile_paper() {
  local wt paper_dir pdf ans
  wt="$1"
  paper_dir="$wt/paper"
  pdf="$paper_dir/main.pdf"

  [[ -f "$paper_dir/main.tex" ]] || die "找不到 $paper_dir/main.tex；说明合并结果不是标准全文结构。"
  say ""
  say "========== 编译 paper/main.tex =========="
  if command -v latexmk >/dev/null 2>&1; then
    if ! (cd "$paper_dir" && latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex); then
      warn "LaTeX 编译失败，但预览 worktree 已保留，正式分支未受影响。"
      say "请把这个日志发给管理员：$paper_dir/main.log"
      exit 3
    fi
  elif command -v xelatex >/dev/null 2>&1; then
    warn "未找到 latexmk，改用 xelatex 连续编译两次。"
    (cd "$paper_dir" && xelatex -interaction=nonstopmode -halt-on-error main.tex && xelatex -interaction=nonstopmode -halt-on-error main.tex) \
      || { warn "LaTeX 编译失败。日志：$paper_dir/main.log"; exit 3; }
  else
    warn "未检测到 latexmk/xelatex。合并已经完成，但本机无法自动编译。"
    say "全文入口：$paper_dir/main.tex"
    return 0
  fi

  say ""
  say "=========================================="
  say "全文预览生成完成"
  say "PDF：$pdf"
  say "=========================================="
  if [[ -f "$pdf" ]]; then
    read -r -p "现在打开 PDF？[Y/n] " ans
    if [[ ! "${ans:-Y}" =~ ^[Nn]$ ]]; then
      open_pdf "$pdf"
    fi
  fi
}

main() {
  local root current old_wt preview_dir stamp branch prefix choice ans
  root="$(repo_root)" || die "当前目录不是 Git 仓库。请在任一正常 worktree 中运行本脚本。若刚才清理预览失败，请先 cd 到正常 worktree。"
  cd "$root" || die "无法进入仓库根目录。"

  if [[ "${1:-}" == "--clean" ]]; then
    clean_preview
  fi

  current="$(git branch --show-current)"
  if [[ "$current" == "$PREVIEW_BRANCH" ]]; then
    die "你现在就在临时预览分支里。正常生成预览请回到自己的正常 worktree；若只是清理，请使用 --clean。"
  fi

  say "========== 本地全文 Merge 预览 =========="
  say "当前工作目录：$root"
  say "当前分支：${current:-<detached HEAD>}"
  say ""
  say "本脚本只创建本地临时 worktree；不会 push，不会修改 main，也不会改你当前工作区。"

  say ""
  say "[1/6] 获取远端最新状态..."
  git fetch "$REMOTE" --prune || die "git fetch 失败，请检查网络或 GitHub 权限。"

  git show-ref --verify --quiet "refs/remotes/${BASE_REMOTE}" \
    || die "找不到基底分支 ${BASE_REMOTE}。"
  for branch in "${MERGE_BRANCHES[@]}"; do
    git show-ref --verify --quiet "refs/remotes/${branch}" \
      || die "找不到远端分支 ${branch}。请把这条报错发给管理员。"
  done

  old_wt="$(preview_worktree_for_branch || true)"
  if [[ -n "$old_wt" ]]; then
    say ""
    say "检测到上一次全文预览：$old_wt"
    say "请选择："
    say "  1) 删除旧预览并重新生成（推荐）"
    say "  2) 直接打开旧 PDF，不重新合并"
    say "  3) 退出"
    read -r -p "输入 1/2/3 [默认 1]：" choice
    choice="${choice:-1}"
    case "$choice" in
      1)
        if [[ -n "$(git -C "$old_wt" status --porcelain 2>/dev/null || true)" ]]; then
          warn "旧预览目录里有未提交改动/未完成合并。这里原则上不应该手改。"
          read -r -p "直接丢弃旧临时预览并重建？[Y/n] " ans
          [[ ! "${ans:-Y}" =~ ^[Nn]$ ]] || { say "已取消。"; exit 0; }
        fi
        remove_preview_worktree_safely "$old_wt"
        git branch -D "$PREVIEW_BRANCH" >/dev/null 2>&1 || true
        ;;
      2)
        open_pdf "$old_wt/paper/main.pdf"
        exit 0
        ;;
      *)
        say "已退出。"
        exit 0
        ;;
    esac
  elif git show-ref --verify --quiet "refs/heads/${PREVIEW_BRANCH}"; then
    warn "发现残留的本地临时 branch，但没有对应 worktree。将只删除这个临时 branch 后重建。"
    git branch -D "$PREVIEW_BRANCH" >/dev/null 2>&1 || die "无法删除残留临时 branch。"
  fi

  preview_dir="$(suggest_preview_dir "$root")"
  if [[ -e "$preview_dir" ]]; then
    stamp="$(date +%Y%m%d-%H%M%S)"
    preview_dir="${preview_dir}-${stamp}"
    warn "默认预览目录已被普通文件/目录占用，改用：$preview_dir"
  fi

  say ""
  say "[2/6] 创建一次性本地预览 worktree..."
  say "基底：$BASE_REMOTE"
  say "目录：$preview_dir"
  git worktree add -b "$PREVIEW_BRANCH" "$preview_dir" "$BASE_REMOTE" \
    || die "创建预览 worktree 失败。"

  say ""
  say "[3/6] 依次合并正式模块分支..."
  for branch in "${MERGE_BRANCHES[@]}"; do
    say ""
    say "---- 合并 $branch ----"
    if git -C "$preview_dir" merge --no-ff --no-edit "$branch"; then
      say "完成：$branch"
      continue
    fi

    if [[ -z "$(git -C "$preview_dir" diff --name-only --diff-filter=U)" ]]; then
      die "合并 ${branch} 失败，但没有检测到普通文本冲突。预览目录已保留：$preview_dir"
    fi

    prefix="$(owned_prefix_for "$branch")"
    resolve_expected_conflicts "$preview_dir" "$branch" "$prefix"
    finish_merge_interactively "$preview_dir" "$branch"
  done

  say ""
  say "[4/6] 使用 feature/toc 的模块化入口生成临时 paper/main.tex..."
  materialize_modular_entry "$preview_dir"

  say ""
  say "[5/6] 检查最终状态..."
  if [[ -n "$(git -C "$preview_dir" status --porcelain)" ]]; then
    git -C "$preview_dir" status --short
  else
    say "临时预览工作区状态：干净。"
  fi
  say "详细临时 merge 历史不在终端展开。"

  say ""
  say "[6/6] 编译全文..."
  compile_paper "$preview_dir"

  say ""
  say "临时预览 branch：$PREVIEW_BRANCH"
  say "临时预览 worktree：$preview_dir"
  say "不要 push 这个 preview 分支。"
  say "看完以后可运行："
  say "  bash <(git show origin/feature/paper-common-final:preview_merge.sh) --clean"
}

main "$@"
