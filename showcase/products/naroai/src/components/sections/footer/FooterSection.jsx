import { useState } from "react";

function NaroMark() {
  return (
    <svg className="h-6 w-auto text-white" viewBox="0 0 256 256" aria-label="Naro">
      <g fill="currentColor" transform="translate(0,256) scale(0.1,-0.1)">
        <path d="M583 1846 c-271 -62 -435 -279 -420 -556 13 -247 166 -429 411 -489 64 -16 131 -17 726 -16 l655 2 78 27 c236 80 367 264 367 514 0 260 -168 463 -430 518 -64 14 -112 15 -320 7 -300 -10 -434 -10 -755 -1 -201 6 -262 5 -312 -6z m497 -76 c96 -4 291 -3 465 3 333 12 386 6 501 -50 268 -131 330 -502 119 -719 -58 -59 -171 -118 -255 -132 -30 -5 -327 -8 -660 -7 -589 2 -607 3 -664 24 -77 27 -131 60 -180 108 -214 209 -167 576 91 716 120 65 223 75 583 57z" />
        <path d="M1205 1505 c-54 -19 -110 -83 -125 -143 -33 -138 87 -268 229 -248 120 16 203 138 171 251 -33 119 -157 182 -275 140z" />
      </g>
    </svg>
  );
}

export default function FooterSection() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  return (
    <footer data-pwc-critical="footer-1" className="min-h-[728px] bg-[#0a0a0a] px-6 pb-10 pt-20 font-sans text-zinc-400">
      <div className="mx-auto flex max-w-6xl flex-col gap-16">
        <div className="flex flex-col items-start justify-between gap-12 md:flex-row">
          <div className="max-w-md">
            <h3 className="mb-4 text-lg font-medium text-white">Get updated from Naro</h3>
            <p className="text-sm leading-relaxed text-zinc-500">
              By signing up, you agree to receive product updates and announcements from Naro. You can opt out at any time via the unsubscribe link in our emails. Your subscription is subject to our{" "}
              <a className="underline hover:text-zinc-300" href="/terms">Terms of Service</a> and{" "}
              <a className="underline hover:text-zinc-300" href="/privacy-policy">Privacy Policy.</a>
            </p>
          </div>
          <form className="mt-2 flex w-full flex-col gap-2 md:mt-0 md:w-auto" onSubmit={(event) => { event.preventDefault(); if (email.trim()) setSubmitted(true); }} noValidate>
            <div className="flex flex-col gap-4 sm:flex-row">
              <input aria-label="Email address" className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-zinc-500 focus:border-white/20 focus:outline-none sm:w-64" placeholder="Email address" type="email" value={email} onChange={(event) => { setEmail(event.target.value); setSubmitted(false); }} />
              <button className="shrink-0 self-start rounded-full border border-white/5 bg-white/10 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-white/20 sm:self-auto" type="submit">Sign up</button>
            </div>
            {submitted && <p className="text-sm text-zinc-400" role="status">Thanks for signing up.</p>}
          </form>
        </div>

        <div className="h-px w-full bg-white/10" />

        <div className="flex flex-col items-start justify-between gap-12 md:flex-row md:gap-0">
          <div className="flex items-center"><NaroMark /></div>
          <div className="grid grid-cols-2 gap-12 text-sm font-medium sm:gap-24">
            <div className="flex flex-col gap-4">
              <a className="transition-colors hover:text-white" href="https://www.youtube.com/@thenaroai" rel="noopener noreferrer" target="_blank">YouTube</a>
              <a className="transition-colors hover:text-white" href="https://www.tiktok.com/@naroai_official" rel="noopener noreferrer" target="_blank">TikTok</a>
              <a className="transition-colors hover:text-white" href="https://x.com/naroai_official" rel="noopener noreferrer" target="_blank">X</a>
              <a className="transition-colors hover:text-white" href="https://www.instagram.com/thenaroai/" rel="noopener noreferrer" target="_blank">Instagram</a>
              <a className="transition-colors hover:text-white" href="https://discord.gg/SRBUFSXd" rel="noopener noreferrer" target="_blank">Discord</a>
            </div>
            <div className="flex flex-col gap-4">
              <a className="transition-colors hover:text-white" href="/privacy-policy">Privacy Policy</a>
              <a className="transition-colors hover:text-white" href="/terms">Terms of Service</a>
            </div>
          </div>
        </div>

        <div className="mt-12 flex flex-col gap-1 pb-8 text-xs text-zinc-600">
          <p>Designed by Naro in California</p>
          <p>Copyright © 2026 Naro AI, Inc. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
