function NaroMark({ className = "" }) {
  return (
    <svg className={className} viewBox="0 0 256 256" aria-hidden="true">
      <g fill="currentColor" transform="translate(0,256) scale(0.1,-0.1)">
        <path d="M583 1846 c-271 -62 -435 -279 -420 -556 13 -247 166 -429 411 -489 64 -16 131 -17 726 -16 l655 2 78 27 c236 80 367 264 367 514 0 260 -168 463 -430 518 -64 14 -112 15 -320 7 -300 -10 -434 -10 -755 -1 -201 6 -262 5 -312 -6z m497 -76 c96 -4 291 -3 465 3 333 12 386 6 501 -50 268 -131 330 -502 119 -719 -58 -59 -171 -118 -255 -132 -30 -5 -327 -8 -660 -7 -589 2 -607 3 -664 24 -77 27 -131 60 -180 108 -214 209 -167 576 91 716 120 65 223 75 583 57z" />
        <path d="M1205 1505 c-54 -19 -110 -83 -125 -143 -33 -138 87 -268 229 -248 120 16 203 138 171 251 -33 119 -157 182 -275 140z" />
      </g>
    </svg>
  );
}

export default function HeaderSection() {
  return (
    <header
      data-pwc-critical="header-1"
      className="fixed inset-x-0 top-0 z-[100] flex w-full justify-center pointer-events-none"
    >
      <div className="pointer-events-auto flex w-full justify-center border-b border-black/10 bg-white/90 backdrop-blur-xl">
        <nav
          data-pwc-critical="navigation-1"
          className="relative z-50 mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8"
        >
          <a className="flex items-center rounded-sm transition-opacity hover:opacity-80" href="/" aria-label="Naro home">
            <span className="relative h-7 w-12 overflow-hidden">
              <NaroMark className="absolute left-1/2 h-14 w-14 -translate-x-1/2 -translate-y-[17px] text-black" />
            </span>
          </a>
          <div className="flex items-center gap-4 sm:gap-6 md:gap-8">
            <a className="text-sm font-medium text-black/50 transition-colors hover:text-black" href="/">Product</a>
            <a className="text-sm font-medium text-black/50 transition-colors hover:text-black" href="/privacy">Privacy</a>
            <a className="text-sm font-medium text-black/50 transition-colors hover:text-black" href="/about">About</a>
            <a href="/order">
              <span className="ml-1 inline-flex h-9 items-center justify-center rounded-full bg-[#141414] px-5 text-sm font-medium text-white shadow-[0_2px_10px_rgba(0,0,0,0.08)] transition-transform hover:scale-105 active:scale-95 sm:ml-2 sm:px-6">Order</span>
            </a>
          </div>
        </nav>
      </div>
    </header>
  );
}
