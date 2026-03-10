-- =========================================================
-- 1. 기본 환경 및 XDG 호환 설정
-- =========================================================
vim.opt.number = true             -- 라인 번호
vim.opt.tabstop = 4               -- 탭 간격
vim.opt.shiftwidth = 4            -- 들여쓰기 간격
vim.opt.expandtab = true          -- 탭을 스페이스로 변환
vim.opt.autoindent = true         -- 자동 들여쓰기
vim.opt.smartindent = true        -- 스마트 들여쓰기
vim.opt.ignorecase = true         -- 대소문자 무시 검색
vim.opt.smartcase = true          -- 대문자 입력 시 대소문자 구분
vim.opt.clipboard = "unnamedplus"-- 시스템 클립보드와 동기화
vim.opt.termguicolors = true      -- 24비트 트루컬러 지원

-- 파일 보호 (Neovim은 자동으로 $XDG_STATE_HOME/nvim/undo 에 저장함)
vim.opt.swapfile = false
vim.opt.backup = false
vim.opt.writebackup = false
vim.opt.undofile = true

-- =========================================================
-- 2. 플러그인 매니저 (lazy.nvim) 부트스트래핑
-- =========================================================
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git", "clone", "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git", "--branch=stable", lazypath
  })
end
vim.opt.rtp:prepend(lazypath)

-- =========================================================
-- 3. 플러그인 설치 및 설정
-- =========================================================
require("lazy").setup({
  -- [테마] TokyoNight (모던 언어 가독성 최상위 테마)
  {
    "folke/tokyonight.nvim",
    lazy = false,
    priority = 1000,
    config = function()
      vim.cmd([[colorscheme tokyonight-night]])
    end,
  },
  -- [하단 상태바] lualine (Airline 대체, 가볍고 빠름)
  {
    "nvim-lualine/lualine.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("lualine").setup({ options = { theme = "tokyonight" } })
    end
  },
  -- [파일 탐색기] nvim-tree (NERDTree 대체)
  {
    "nvim-tree/nvim-tree.lua",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("nvim-tree").setup()
      -- 단축키 F7 매핑
      vim.keymap.set('n', '<F7>', ':NvimTreeToggle<CR>', { noremap = true, silent = true })
    end
  },
  -- [Git 상태] gitsigns (GitGutter 대체)
  {
    "lewis6991/gitsigns.nvim",
    config = function()
      require("gitsigns").setup()
    end
  }
})
