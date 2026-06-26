import { h as handleSplittingInitialized } from "./text-split.js";
import { C as CLASSES } from "./lib/DxoHJvy8.js";
import "./lib/50Lx19ak.js";
var l = Object.defineProperty;
var u = (s, e, t) => e in s ? l(s, e, { enumerable: true, configurable: true, writable: true, value: t }) : s[e] = t;
var i = (s, e, t) => (u(s, typeof e != "symbol" ? e + "" : e, t), t);
const o = {
  marqueeParentSelector: '[data-role="marquee-parent"]',
  marqueeMovingLineSelector: '[data-role="marquee-moving-line"]',
  marqueeListSelector: '[data-role="marquee-list"]',
  duration: 10,
  divisibleNumber: 0,
  matchMediaRule: window.matchMedia("screen"),
  on: {},
  devMode: false
};
class d {
  constructor(e) {
    i(this, "marqueeParentElement");
    i(this, "marqueeMovingLineElement");
    i(this, "marqueeListElement");
    i(this, "numberOfListChildren");
    i(this, "duration");
    i(this, "divisibleNumber");
    i(this, "matchMediaRule");
    i(this, "listsNumber");
    i(this, "fragmentForDuplicate");
    i(this, "on", {});
    i(this, "devMode");
    i(this, "init", () => {
      if (this.on.beforeInit && this.on.beforeInit(this), !this.hasAllRequiredNodes()) {
        if (this.devMode)
          throw new Error("Marquee has not all required nodes");
        return;
      }
      this.addCustomAttributes(), this.initResizeObserver(), this.on.afterInit && this.on.afterInit(this);
    });
    i(this, "initResizeObserver", () => {
      console.log("observer");
      const e2 = new ResizeObserver(() => {
        this.matchMediaRule.matches ? this.update() : this.disable();
      });
      this.marqueeParentElement && e2.observe(this.marqueeParentElement);
    });
    i(this, "hasAllRequiredNodes", () => ![
      this.marqueeParentElement,
      this.marqueeMovingLineElement,
      this.marqueeListElement
    ].some((t2) => !t2));
    i(this, "addCustomAttributes", () => {
      this.marqueeParentElement && (this.marqueeParentElement.dataset.marqueeRole = "parent"), this.marqueeMovingLineElement && (this.marqueeMovingLineElement.dataset.marqueeRole = "moving-line"), this.marqueeListElement && (this.marqueeListElement.dataset.marqueeRole = "list");
    });
    i(this, "getListsNumber", () => {
      let e2 = 0;
      if (!this.marqueeListElement)
        return 2;
      if (Array.from(this.marqueeListElement.children).slice(0, this.numberOfListChildren).forEach((r2) => {
        e2 += r2.clientWidth;
      }), e2 > 0 && this.marqueeParentElement) {
        const { clientWidth: r2 } = this.marqueeParentElement;
        return 2 * Math.ceil(r2 / e2);
      }
      return 2;
    });
    i(this, "greatestCommonDivisor", () => {
      let e2 = this.divisibleNumber, t2 = this.numberOfListChildren || 0;
      for (; t2 !== 0; ) {
        const r2 = t2;
        t2 && (t2 = e2 % t2, e2 = r2);
      }
      return e2;
    });
    i(this, "leastCommonMultiple", () => this.numberOfListChildren ? Math.abs(this.divisibleNumber * this.numberOfListChildren) / this.greatestCommonDivisor() : 0);
    i(this, "getCopyOfFragmentForDuplicate", () => this.fragmentForDuplicate ? this.fragmentForDuplicate : this.generateListElement());
    i(this, "disable", () => {
      this.on.disable && this.on.disable(this), this.listsNumber = 1;
      const e2 = this.getCopyOfFragmentForDuplicate();
      this.marqueeParentElement && (this.marqueeParentElement.dataset.marqueeState = "disabled"), this.marqueeListElement && (this.marqueeListElement.innerHTML = "", this.marqueeListElement.append(e2.cloneNode(true)));
    });
    i(this, "update", () => {
      this.on.update && this.on.update(this), this.marqueeParentElement && (this.marqueeParentElement.dataset.marqueeState = "enabled");
      const e2 = this.getListsNumber();
      let t2 = 1;
      if (e2 === this.listsNumber || !this.numberOfListChildren)
        return;
      const r2 = this.getCopyOfFragmentForDuplicate(), n2 = r2.children.length / this.numberOfListChildren;
      for (this.marqueeListElement && (this.marqueeListElement.innerHTML = "", this.marqueeListElement.append(r2.cloneNode(true))); t2 < e2; )
        this.marqueeListElement && this.marqueeListElement.append(r2.cloneNode(true)), t2 += n2;
      this.marqueeMovingLineElement && (this.marqueeMovingLineElement.style.animationDuration = `${(t2 + n2) * this.duration}s`, this.listsNumber = e2);
    });
    i(this, "generateListElement", () => {
      const e2 = document.createDocumentFragment(), t2 = document.createDocumentFragment();
      if (!this.marqueeListElement)
        return e2;
      const r2 = Array.from(this.marqueeListElement.children).slice(0, this.numberOfListChildren);
      if (this.divisibleNumber > 0) {
        const n2 = this.leastCommonMultiple(), a2 = n2 - r2.length === 0 ? 0 : n2 - r2.length;
        for (let m = 0; m < a2; m += 1)
          t2.append(r2[m % r2.length].cloneNode(true));
      }
      return [...r2, ...Array.from(t2.children)].forEach((n2) => {
        e2.append(n2);
      }), this.fragmentForDuplicate = e2, e2;
    });
    var r, n, a;
    const t = { ...o, ...e };
    this.marqueeParentElement = document.querySelector(t.marqueeParentSelector), this.marqueeMovingLineElement = (r = this.marqueeParentElement) == null ? void 0 : r.querySelector(t.marqueeMovingLineSelector), this.marqueeListElement = (n = this.marqueeParentElement) == null ? void 0 : n.querySelector(t.marqueeListSelector), this.numberOfListChildren = (a = this.marqueeListElement) == null ? void 0 : a.children.length, this.duration = Number.parseInt(window.getComputedStyle(this.marqueeMovingLineElement).animationDuration, 10) || t.duration, this.divisibleNumber = t.divisibleNumber, this.matchMediaRule = t.matchMediaRule, this.listsNumber = 1, this.fragmentForDuplicate = void 0, this.on = t.on, this.devMode = t.devMode;
  }
}
const marquee = ({ widget, isLastHeadingMarquee }) => {
  const { widgetId, widgetDuration, widgetMedia } = widget.dataset;
  const marqueeHeadingInstance = new d({
    marqueeParentSelector: `[data-widget-id="${widgetId}"] [data-role="marquee-parent"]`,
    wrapperOfVisiblePartOfMarquee: widget,
    matchMediaRule: window.matchMedia(widgetMedia ?? "screen"),
    duration: Number(widgetDuration) ?? 10,
    on: {
      afterInit: () => {
        if (!(widget == null ? void 0 : widget.hasAttribute("data-marquee-heading"))) return;
        widget.classList.add(CLASSES.DISABLED);
        if (isLastHeadingMarquee) {
          setTimeout(() => {
            handleSplittingInitialized();
          }, 1e3);
        }
      }
    }
  });
  marqueeHeadingInstance.init();
};
const WIDGET_SELECTOR = '[data-widget="marquee"]';
const WIDGET_FOR_HEADING_SELECTOR = "[data-marquee-heading]";
const widgets = document.querySelectorAll(WIDGET_SELECTOR);
const widgetsForHeading = document.querySelectorAll(WIDGET_FOR_HEADING_SELECTOR);
widgets.forEach((widget) => {
  const isLastHeadingMarquee = widget.hasAttribute("data-marquee-heading") && Array.from(widgetsForHeading).indexOf(widget) === widgetsForHeading.length - 1;
  marquee({ widget, isLastHeadingMarquee });
});
