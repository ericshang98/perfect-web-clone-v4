var __defProp = Object.defineProperty;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __publicField = (obj, key, value) => __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);
import { g as gsapWithCSS } from "./lib/50Lx19ak.js";
import { S as ScrollTrigger } from "./lib/C6o_azLH.js";
import { C as CLASSES } from "./lib/DxoHJvy8.js";
var version = "1.3.17";
function clamp(min, input, max) {
  return Math.max(min, Math.min(input, max));
}
function lerp(x, y, t) {
  return (1 - t) * x + t * y;
}
function damp(x, y, lambda, deltaTime) {
  return lerp(x, y, 1 - Math.exp(-lambda * deltaTime));
}
function modulo(n, d) {
  return (n % d + d) % d;
}
var Animate = class {
  constructor() {
    __publicField(this, "isRunning", false);
    __publicField(this, "value", 0);
    __publicField(this, "from", 0);
    __publicField(this, "to", 0);
    __publicField(this, "currentTime", 0);
    // These are instanciated in the fromTo method
    __publicField(this, "lerp");
    __publicField(this, "duration");
    __publicField(this, "easing");
    __publicField(this, "onUpdate");
  }
  /**
   * Advance the animation by the given delta time
   *
   * @param deltaTime - The time in seconds to advance the animation
   */
  advance(deltaTime) {
    var _a;
    if (!this.isRunning) return;
    let completed = false;
    if (this.duration && this.easing) {
      this.currentTime += deltaTime;
      const linearProgress = clamp(0, this.currentTime / this.duration, 1);
      completed = linearProgress >= 1;
      const easedProgress = completed ? 1 : this.easing(linearProgress);
      this.value = this.from + (this.to - this.from) * easedProgress;
    } else if (this.lerp) {
      this.value = damp(this.value, this.to, this.lerp * 60, deltaTime);
      if (Math.round(this.value) === this.to) {
        this.value = this.to;
        completed = true;
      }
    } else {
      this.value = this.to;
      completed = true;
    }
    if (completed) {
      this.stop();
    }
    (_a = this.onUpdate) == null ? void 0 : _a.call(this, this.value, completed);
  }
  /** Stop the animation */
  stop() {
    this.isRunning = false;
  }
  /**
   * Set up the animation from a starting value to an ending value
   * with optional parameters for lerping, duration, easing, and onUpdate callback
   *
   * @param from - The starting value
   * @param to - The ending value
   * @param options - Options for the animation
   */
  fromTo(from, to, { lerp: lerp2, duration, easing, onStart, onUpdate }) {
    this.from = this.value = from;
    this.to = to;
    this.lerp = lerp2;
    this.duration = duration;
    this.easing = easing;
    this.currentTime = 0;
    this.isRunning = true;
    onStart == null ? void 0 : onStart();
    this.onUpdate = onUpdate;
  }
};
function debounce(callback, delay) {
  let timer;
  return function(...args) {
    let context = this;
    clearTimeout(timer);
    timer = setTimeout(() => {
      timer = void 0;
      callback.apply(context, args);
    }, delay);
  };
}
var Dimensions = class {
  constructor(wrapper, content, { autoResize = true, debounce: debounceValue = 250 } = {}) {
    __publicField(this, "width", 0);
    __publicField(this, "height", 0);
    __publicField(this, "scrollHeight", 0);
    __publicField(this, "scrollWidth", 0);
    // These are instanciated in the constructor as they need information from the options
    __publicField(this, "debouncedResize");
    __publicField(this, "wrapperResizeObserver");
    __publicField(this, "contentResizeObserver");
    __publicField(this, "resize", () => {
      this.onWrapperResize();
      this.onContentResize();
    });
    __publicField(this, "onWrapperResize", () => {
      if (this.wrapper instanceof Window) {
        this.width = window.innerWidth;
        this.height = window.innerHeight;
      } else {
        this.width = this.wrapper.clientWidth;
        this.height = this.wrapper.clientHeight;
      }
    });
    __publicField(this, "onContentResize", () => {
      if (this.wrapper instanceof Window) {
        this.scrollHeight = this.content.scrollHeight;
        this.scrollWidth = this.content.scrollWidth;
      } else {
        this.scrollHeight = this.wrapper.scrollHeight;
        this.scrollWidth = this.wrapper.scrollWidth;
      }
    });
    this.wrapper = wrapper;
    this.content = content;
    if (autoResize) {
      this.debouncedResize = debounce(this.resize, debounceValue);
      if (this.wrapper instanceof Window) {
        window.addEventListener("resize", this.debouncedResize, false);
      } else {
        this.wrapperResizeObserver = new ResizeObserver(this.debouncedResize);
        this.wrapperResizeObserver.observe(this.wrapper);
      }
      this.contentResizeObserver = new ResizeObserver(this.debouncedResize);
      this.contentResizeObserver.observe(this.content);
    }
    this.resize();
  }
  destroy() {
    var _a, _b;
    (_a = this.wrapperResizeObserver) == null ? void 0 : _a.disconnect();
    (_b = this.contentResizeObserver) == null ? void 0 : _b.disconnect();
    if (this.wrapper === window && this.debouncedResize) {
      window.removeEventListener("resize", this.debouncedResize, false);
    }
  }
  get limit() {
    return {
      x: this.scrollWidth - this.width,
      y: this.scrollHeight - this.height
    };
  }
};
var Emitter = class {
  constructor() {
    __publicField(this, "events", {});
  }
  /**
   * Emit an event with the given data
   * @param event Event name
   * @param args Data to pass to the event handlers
   */
  emit(event, ...args) {
    var _a;
    let callbacks = this.events[event] || [];
    for (let i = 0, length = callbacks.length; i < length; i++) {
      (_a = callbacks[i]) == null ? void 0 : _a.call(callbacks, ...args);
    }
  }
  /**
   * Add a callback to the event
   * @param event Event name
   * @param cb Callback function
   * @returns Unsubscribe function
   */
  on(event, cb) {
    var _a;
    ((_a = this.events[event]) == null ? void 0 : _a.push(cb)) || (this.events[event] = [cb]);
    return () => {
      var _a2;
      this.events[event] = (_a2 = this.events[event]) == null ? void 0 : _a2.filter((i) => cb !== i);
    };
  }
  /**
   * Remove a callback from the event
   * @param event Event name
   * @param callback Callback function
   */
  off(event, callback) {
    var _a;
    this.events[event] = (_a = this.events[event]) == null ? void 0 : _a.filter((i) => callback !== i);
  }
  /**
   * Remove all event listeners and clean up
   */
  destroy() {
    this.events = {};
  }
};
var LINE_HEIGHT = 100 / 6;
var listenerOptions = { passive: false };
var VirtualScroll = class {
  constructor(element, options = { wheelMultiplier: 1, touchMultiplier: 1 }) {
    __publicField(this, "touchStart", {
      x: 0,
      y: 0
    });
    __publicField(this, "lastDelta", {
      x: 0,
      y: 0
    });
    __publicField(this, "window", {
      width: 0,
      height: 0
    });
    __publicField(this, "emitter", new Emitter());
    /**
     * Event handler for 'touchstart' event
     *
     * @param event Touch event
     */
    __publicField(this, "onTouchStart", (event) => {
      const { clientX, clientY } = event.targetTouches ? event.targetTouches[0] : event;
      this.touchStart.x = clientX;
      this.touchStart.y = clientY;
      this.lastDelta = {
        x: 0,
        y: 0
      };
      this.emitter.emit("scroll", {
        deltaX: 0,
        deltaY: 0,
        event
      });
    });
    /** Event handler for 'touchmove' event */
    __publicField(this, "onTouchMove", (event) => {
      const { clientX, clientY } = event.targetTouches ? event.targetTouches[0] : event;
      const deltaX = -(clientX - this.touchStart.x) * this.options.touchMultiplier;
      const deltaY = -(clientY - this.touchStart.y) * this.options.touchMultiplier;
      this.touchStart.x = clientX;
      this.touchStart.y = clientY;
      this.lastDelta = {
        x: deltaX,
        y: deltaY
      };
      this.emitter.emit("scroll", {
        deltaX,
        deltaY,
        event
      });
    });
    __publicField(this, "onTouchEnd", (event) => {
      this.emitter.emit("scroll", {
        deltaX: this.lastDelta.x,
        deltaY: this.lastDelta.y,
        event
      });
    });
    /** Event handler for 'wheel' event */
    __publicField(this, "onWheel", (event) => {
      let { deltaX, deltaY, deltaMode } = event;
      const multiplierX = deltaMode === 1 ? LINE_HEIGHT : deltaMode === 2 ? this.window.width : 1;
      const multiplierY = deltaMode === 1 ? LINE_HEIGHT : deltaMode === 2 ? this.window.height : 1;
      deltaX *= multiplierX;
      deltaY *= multiplierY;
      deltaX *= this.options.wheelMultiplier;
      deltaY *= this.options.wheelMultiplier;
      this.emitter.emit("scroll", { deltaX, deltaY, event });
    });
    __publicField(this, "onWindowResize", () => {
      this.window = {
        width: window.innerWidth,
        height: window.innerHeight
      };
    });
    this.element = element;
    this.options = options;
    window.addEventListener("resize", this.onWindowResize, false);
    this.onWindowResize();
    this.element.addEventListener("wheel", this.onWheel, listenerOptions);
    this.element.addEventListener(
      "touchstart",
      this.onTouchStart,
      listenerOptions
    );
    this.element.addEventListener(
      "touchmove",
      this.onTouchMove,
      listenerOptions
    );
    this.element.addEventListener("touchend", this.onTouchEnd, listenerOptions);
  }
  /**
   * Add an event listener for the given event and callback
   *
   * @param event Event name
   * @param callback Callback function
   */
  on(event, callback) {
    return this.emitter.on(event, callback);
  }
  /** Remove all event listeners and clean up */
  destroy() {
    this.emitter.destroy();
    window.removeEventListener("resize", this.onWindowResize, false);
    this.element.removeEventListener("wheel", this.onWheel, listenerOptions);
    this.element.removeEventListener(
      "touchstart",
      this.onTouchStart,
      listenerOptions
    );
    this.element.removeEventListener(
      "touchmove",
      this.onTouchMove,
      listenerOptions
    );
    this.element.removeEventListener(
      "touchend",
      this.onTouchEnd,
      listenerOptions
    );
  }
};
var defaultEasing = (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t));
var Lenis = class {
  constructor({
    wrapper = window,
    content = document.documentElement,
    eventsTarget = wrapper,
    smoothWheel = true,
    syncTouch = false,
    syncTouchLerp = 0.075,
    touchInertiaExponent = 1.7,
    duration,
    // in seconds
    easing,
    lerp: lerp2 = 0.1,
    infinite = false,
    orientation = "vertical",
    // vertical, horizontal
    gestureOrientation = orientation === "horizontal" ? "both" : "vertical",
    // vertical, horizontal, both
    touchMultiplier = 1,
    wheelMultiplier = 1,
    autoResize = true,
    prevent,
    virtualScroll,
    overscroll = true,
    autoRaf = false,
    anchors = false,
    autoToggle = false,
    // https://caniuse.com/?search=transition-behavior
    allowNestedScroll = false,
    // @ts-ignore: this will be deprecated in the future
    __experimental__naiveDimensions = false,
    naiveDimensions = __experimental__naiveDimensions,
    stopInertiaOnNavigate = false
  } = {}) {
    __publicField(this, "_isScrolling", false);
    // true when scroll is animating
    __publicField(this, "_isStopped", false);
    // true if user should not be able to scroll - enable/disable programmatically
    __publicField(this, "_isLocked", false);
    // same as isStopped but enabled/disabled when scroll reaches target
    __publicField(this, "_preventNextNativeScrollEvent", false);
    __publicField(this, "_resetVelocityTimeout", null);
    __publicField(this, "_rafId", null);
    /**
     * Whether or not the user is touching the screen
     */
    __publicField(this, "isTouching");
    /**
     * The time in ms since the lenis instance was created
     */
    __publicField(this, "time", 0);
    /**
     * User data that will be forwarded through the scroll event
     *
     * @example
     * lenis.scrollTo(100, {
     *   userData: {
     *     foo: 'bar'
     *   }
     * })
     */
    __publicField(this, "userData", {});
    /**
     * The last velocity of the scroll
     */
    __publicField(this, "lastVelocity", 0);
    /**
     * The current velocity of the scroll
     */
    __publicField(this, "velocity", 0);
    /**
     * The direction of the scroll
     */
    __publicField(this, "direction", 0);
    /**
     * The options passed to the lenis instance
     */
    __publicField(this, "options");
    /**
     * The target scroll value
     */
    __publicField(this, "targetScroll");
    /**
     * The animated scroll value
     */
    __publicField(this, "animatedScroll");
    // These are instanciated here as they don't need information from the options
    __publicField(this, "animate", new Animate());
    __publicField(this, "emitter", new Emitter());
    // These are instanciated in the constructor as they need information from the options
    __publicField(this, "dimensions");
    // This is not private because it's used in the Snap class
    __publicField(this, "virtualScroll");
    __publicField(this, "onScrollEnd", (e) => {
      if (!(e instanceof CustomEvent)) {
        if (this.isScrolling === "smooth" || this.isScrolling === false) {
          e.stopPropagation();
        }
      }
    });
    __publicField(this, "dispatchScrollendEvent", () => {
      this.options.wrapper.dispatchEvent(
        new CustomEvent("scrollend", {
          bubbles: this.options.wrapper === window,
          // cancelable: false,
          detail: {
            lenisScrollEnd: true
          }
        })
      );
    });
    __publicField(this, "onTransitionEnd", (event) => {
      if (event.propertyName.includes("overflow")) {
        this.checkOverflow();
      }
    });
    __publicField(this, "onClick", (event) => {
      const path = event.composedPath();
      const anchorElements = path.filter(
        (node) => node instanceof HTMLAnchorElement && node.getAttribute("href")
      );
      if (this.options.anchors) {
        const anchor = anchorElements.find(
          (node) => {
            var _a;
            return (_a = node.getAttribute("href")) == null ? void 0 : _a.includes("#");
          }
        );
        if (anchor) {
          const href = anchor.getAttribute("href");
          if (href) {
            const options = typeof this.options.anchors === "object" && this.options.anchors ? this.options.anchors : void 0;
            const target = `#${href.split("#")[1]}`;
            this.scrollTo(target, options);
          }
        }
      }
      if (this.options.stopInertiaOnNavigate) {
        const internalLink = anchorElements.find(
          (node) => node.host === window.location.host
        );
        if (internalLink) {
          this.reset();
        }
      }
    });
    __publicField(this, "onPointerDown", (event) => {
      if (event.button === 1) {
        this.reset();
      }
    });
    __publicField(this, "onVirtualScroll", (data) => {
      if (typeof this.options.virtualScroll === "function" && this.options.virtualScroll(data) === false)
        return;
      const { deltaX, deltaY, event } = data;
      this.emitter.emit("virtual-scroll", { deltaX, deltaY, event });
      if (event.ctrlKey) return;
      if (event.lenisStopPropagation) return;
      const isTouch = event.type.includes("touch");
      const isWheel = event.type.includes("wheel");
      this.isTouching = event.type === "touchstart" || event.type === "touchmove";
      const isClickOrTap = deltaX === 0 && deltaY === 0;
      const isTapToStop = this.options.syncTouch && isTouch && event.type === "touchstart" && isClickOrTap && !this.isStopped && !this.isLocked;
      if (isTapToStop) {
        this.reset();
        return;
      }
      const isUnknownGesture = this.options.gestureOrientation === "vertical" && deltaY === 0 || this.options.gestureOrientation === "horizontal" && deltaX === 0;
      if (isClickOrTap || isUnknownGesture) {
        return;
      }
      let composedPath = event.composedPath();
      composedPath = composedPath.slice(0, composedPath.indexOf(this.rootElement));
      const prevent = this.options.prevent;
      if (!!composedPath.find(
        (node) => {
          var _a, _b, _c;
          return node instanceof HTMLElement && (typeof prevent === "function" && (prevent == null ? void 0 : prevent(node)) || ((_a = node.hasAttribute) == null ? void 0 : _a.call(node, "data-lenis-prevent")) || isTouch && ((_b = node.hasAttribute) == null ? void 0 : _b.call(node, "data-lenis-prevent-touch")) || isWheel && ((_c = node.hasAttribute) == null ? void 0 : _c.call(node, "data-lenis-prevent-wheel")) || this.options.allowNestedScroll && this.checkNestedScroll(node, { deltaX, deltaY }));
        }
      ))
        return;
      if (this.isStopped || this.isLocked) {
        if (event.cancelable) {
          event.preventDefault();
        }
        return;
      }
      const isSmooth = this.options.syncTouch && isTouch || this.options.smoothWheel && isWheel;
      if (!isSmooth) {
        this.isScrolling = "native";
        this.animate.stop();
        event.lenisStopPropagation = true;
        return;
      }
      let delta = deltaY;
      if (this.options.gestureOrientation === "both") {
        delta = Math.abs(deltaY) > Math.abs(deltaX) ? deltaY : deltaX;
      } else if (this.options.gestureOrientation === "horizontal") {
        delta = deltaX;
      }
      if (!this.options.overscroll || this.options.infinite || this.options.wrapper !== window && this.limit > 0 && (this.animatedScroll > 0 && this.animatedScroll < this.limit || this.animatedScroll === 0 && deltaY > 0 || this.animatedScroll === this.limit && deltaY < 0)) {
        event.lenisStopPropagation = true;
      }
      if (event.cancelable) {
        event.preventDefault();
      }
      const isSyncTouch = isTouch && this.options.syncTouch;
      const isTouchEnd = isTouch && event.type === "touchend";
      const hasTouchInertia = isTouchEnd;
      if (hasTouchInertia) {
        delta = Math.sign(this.velocity) * Math.pow(Math.abs(this.velocity), this.options.touchInertiaExponent);
      }
      this.scrollTo(this.targetScroll + delta, {
        programmatic: false,
        ...isSyncTouch ? {
          lerp: hasTouchInertia ? this.options.syncTouchLerp : 1
        } : {
          lerp: this.options.lerp,
          duration: this.options.duration,
          easing: this.options.easing
        }
      });
    });
    __publicField(this, "onNativeScroll", () => {
      if (this._resetVelocityTimeout !== null) {
        clearTimeout(this._resetVelocityTimeout);
        this._resetVelocityTimeout = null;
      }
      if (this._preventNextNativeScrollEvent) {
        this._preventNextNativeScrollEvent = false;
        return;
      }
      if (this.isScrolling === false || this.isScrolling === "native") {
        const lastScroll = this.animatedScroll;
        this.animatedScroll = this.targetScroll = this.actualScroll;
        this.lastVelocity = this.velocity;
        this.velocity = this.animatedScroll - lastScroll;
        this.direction = Math.sign(
          this.animatedScroll - lastScroll
        );
        if (!this.isStopped) {
          this.isScrolling = "native";
        }
        this.emit();
        if (this.velocity !== 0) {
          this._resetVelocityTimeout = setTimeout(() => {
            this.lastVelocity = this.velocity;
            this.velocity = 0;
            this.isScrolling = false;
            this.emit();
          }, 400);
        }
      }
    });
    /**
     * RequestAnimationFrame for lenis
     *
     * @param time The time in ms from an external clock like `requestAnimationFrame` or Tempus
     */
    __publicField(this, "raf", (time) => {
      const deltaTime = time - (this.time || time);
      this.time = time;
      this.animate.advance(deltaTime * 1e-3);
      if (this.options.autoRaf) {
        this._rafId = requestAnimationFrame(this.raf);
      }
    });
    window.lenisVersion = version;
    if (!wrapper || wrapper === document.documentElement) {
      wrapper = window;
    }
    if (typeof duration === "number" && typeof easing !== "function") {
      easing = defaultEasing;
    } else if (typeof easing === "function" && typeof duration !== "number") {
      duration = 1;
    }
    this.options = {
      wrapper,
      content,
      eventsTarget,
      smoothWheel,
      syncTouch,
      syncTouchLerp,
      touchInertiaExponent,
      duration,
      easing,
      lerp: lerp2,
      infinite,
      gestureOrientation,
      orientation,
      touchMultiplier,
      wheelMultiplier,
      autoResize,
      prevent,
      virtualScroll,
      overscroll,
      autoRaf,
      anchors,
      autoToggle,
      allowNestedScroll,
      naiveDimensions,
      stopInertiaOnNavigate
    };
    this.dimensions = new Dimensions(wrapper, content, { autoResize });
    this.updateClassName();
    this.targetScroll = this.animatedScroll = this.actualScroll;
    this.options.wrapper.addEventListener("scroll", this.onNativeScroll, false);
    this.options.wrapper.addEventListener("scrollend", this.onScrollEnd, {
      capture: true
    });
    if (this.options.anchors || this.options.stopInertiaOnNavigate) {
      this.options.wrapper.addEventListener(
        "click",
        this.onClick,
        false
      );
    }
    this.options.wrapper.addEventListener(
      "pointerdown",
      this.onPointerDown,
      false
    );
    this.virtualScroll = new VirtualScroll(eventsTarget, {
      touchMultiplier,
      wheelMultiplier
    });
    this.virtualScroll.on("scroll", this.onVirtualScroll);
    if (this.options.autoToggle) {
      this.checkOverflow();
      this.rootElement.addEventListener("transitionend", this.onTransitionEnd, {
        passive: true
      });
    }
    if (this.options.autoRaf) {
      this._rafId = requestAnimationFrame(this.raf);
    }
  }
  /**
   * Destroy the lenis instance, remove all event listeners and clean up the class name
   */
  destroy() {
    this.emitter.destroy();
    this.options.wrapper.removeEventListener(
      "scroll",
      this.onNativeScroll,
      false
    );
    this.options.wrapper.removeEventListener("scrollend", this.onScrollEnd, {
      capture: true
    });
    this.options.wrapper.removeEventListener(
      "pointerdown",
      this.onPointerDown,
      false
    );
    if (this.options.anchors || this.options.stopInertiaOnNavigate) {
      this.options.wrapper.removeEventListener(
        "click",
        this.onClick,
        false
      );
    }
    this.virtualScroll.destroy();
    this.dimensions.destroy();
    this.cleanUpClassName();
    if (this._rafId) {
      cancelAnimationFrame(this._rafId);
    }
  }
  on(event, callback) {
    return this.emitter.on(event, callback);
  }
  off(event, callback) {
    return this.emitter.off(event, callback);
  }
  get overflow() {
    const property = this.isHorizontal ? "overflow-x" : "overflow-y";
    return getComputedStyle(this.rootElement)[property];
  }
  checkOverflow() {
    if (["hidden", "clip"].includes(this.overflow)) {
      this.internalStop();
    } else {
      this.internalStart();
    }
  }
  setScroll(scroll) {
    if (this.isHorizontal) {
      this.options.wrapper.scrollTo({ left: scroll, behavior: "instant" });
    } else {
      this.options.wrapper.scrollTo({ top: scroll, behavior: "instant" });
    }
  }
  /**
   * Force lenis to recalculate the dimensions
   */
  resize() {
    this.dimensions.resize();
    this.animatedScroll = this.targetScroll = this.actualScroll;
    this.emit();
  }
  emit() {
    this.emitter.emit("scroll", this);
  }
  reset() {
    this.isLocked = false;
    this.isScrolling = false;
    this.animatedScroll = this.targetScroll = this.actualScroll;
    this.lastVelocity = this.velocity = 0;
    this.animate.stop();
  }
  /**
   * Start lenis scroll after it has been stopped
   */
  start() {
    if (!this.isStopped) return;
    if (this.options.autoToggle) {
      this.rootElement.style.removeProperty("overflow");
      return;
    }
    this.internalStart();
  }
  internalStart() {
    if (!this.isStopped) return;
    this.reset();
    this.isStopped = false;
    this.emit();
  }
  /**
   * Stop lenis scroll
   */
  stop() {
    if (this.isStopped) return;
    if (this.options.autoToggle) {
      this.rootElement.style.setProperty("overflow", "clip");
      return;
    }
    this.internalStop();
  }
  internalStop() {
    if (this.isStopped) return;
    this.reset();
    this.isStopped = true;
    this.emit();
  }
  /**
   * Scroll to a target value
   *
   * @param target The target value to scroll to
   * @param options The options for the scroll
   *
   * @example
   * lenis.scrollTo(100, {
   *   offset: 100,
   *   duration: 1,
   *   easing: (t) => 1 - Math.cos((t * Math.PI) / 2),
   *   lerp: 0.1,
   *   onStart: () => {
   *     console.log('onStart')
   *   },
   *   onComplete: () => {
   *     console.log('onComplete')
   *   },
   * })
   */
  scrollTo(target, {
    offset = 0,
    immediate = false,
    lock = false,
    programmatic = true,
    // called from outside of the class
    lerp: lerp2 = programmatic ? this.options.lerp : void 0,
    duration = programmatic ? this.options.duration : void 0,
    easing = programmatic ? this.options.easing : void 0,
    onStart,
    onComplete,
    force = false,
    // scroll even if stopped
    userData
  } = {}) {
    if ((this.isStopped || this.isLocked) && !force) return;
    if (typeof target === "string" && ["top", "left", "start", "#"].includes(target)) {
      target = 0;
    } else if (typeof target === "string" && ["bottom", "right", "end"].includes(target)) {
      target = this.limit;
    } else {
      let node;
      if (typeof target === "string") {
        node = document.querySelector(target);
        if (!node) {
          if (target === "#top") {
            target = 0;
          } else {
            console.warn("Lenis: Target not found", target);
          }
        }
      } else if (target instanceof HTMLElement && (target == null ? void 0 : target.nodeType)) {
        node = target;
      }
      if (node) {
        if (this.options.wrapper !== window) {
          const wrapperRect = this.rootElement.getBoundingClientRect();
          offset -= this.isHorizontal ? wrapperRect.left : wrapperRect.top;
        }
        const rect = node.getBoundingClientRect();
        target = (this.isHorizontal ? rect.left : rect.top) + this.animatedScroll;
      }
    }
    if (typeof target !== "number") return;
    target += offset;
    target = Math.round(target);
    if (this.options.infinite) {
      if (programmatic) {
        this.targetScroll = this.animatedScroll = this.scroll;
        const distance = target - this.animatedScroll;
        if (distance > this.limit / 2) {
          target = target - this.limit;
        } else if (distance < -this.limit / 2) {
          target = target + this.limit;
        }
      }
    } else {
      target = clamp(0, target, this.limit);
    }
    if (target === this.targetScroll) {
      onStart == null ? void 0 : onStart(this);
      onComplete == null ? void 0 : onComplete(this);
      return;
    }
    this.userData = userData ?? {};
    if (immediate) {
      this.animatedScroll = this.targetScroll = target;
      this.setScroll(this.scroll);
      this.reset();
      this.preventNextNativeScrollEvent();
      this.emit();
      onComplete == null ? void 0 : onComplete(this);
      this.userData = {};
      requestAnimationFrame(() => {
        this.dispatchScrollendEvent();
      });
      return;
    }
    if (!programmatic) {
      this.targetScroll = target;
    }
    if (typeof duration === "number" && typeof easing !== "function") {
      easing = defaultEasing;
    } else if (typeof easing === "function" && typeof duration !== "number") {
      duration = 1;
    }
    this.animate.fromTo(this.animatedScroll, target, {
      duration,
      easing,
      lerp: lerp2,
      onStart: () => {
        if (lock) this.isLocked = true;
        this.isScrolling = "smooth";
        onStart == null ? void 0 : onStart(this);
      },
      onUpdate: (value, completed) => {
        this.isScrolling = "smooth";
        this.lastVelocity = this.velocity;
        this.velocity = value - this.animatedScroll;
        this.direction = Math.sign(this.velocity);
        this.animatedScroll = value;
        this.setScroll(this.scroll);
        if (programmatic) {
          this.targetScroll = value;
        }
        if (!completed) this.emit();
        if (completed) {
          this.reset();
          this.emit();
          onComplete == null ? void 0 : onComplete(this);
          this.userData = {};
          requestAnimationFrame(() => {
            this.dispatchScrollendEvent();
          });
          this.preventNextNativeScrollEvent();
        }
      }
    });
  }
  preventNextNativeScrollEvent() {
    this._preventNextNativeScrollEvent = true;
    requestAnimationFrame(() => {
      this._preventNextNativeScrollEvent = false;
    });
  }
  checkNestedScroll(node, { deltaX, deltaY }) {
    const time = Date.now();
    const cache = node._lenis ?? (node._lenis = {});
    let hasOverflowX, hasOverflowY, isScrollableX, isScrollableY, scrollWidth, scrollHeight, clientWidth, clientHeight;
    const gestureOrientation = this.options.gestureOrientation;
    if (time - (cache.time ?? 0) > 2e3) {
      cache.time = Date.now();
      const computedStyle = window.getComputedStyle(node);
      cache.computedStyle = computedStyle;
      const overflowXString = computedStyle.overflowX;
      const overflowYString = computedStyle.overflowY;
      hasOverflowX = ["auto", "overlay", "scroll"].includes(overflowXString);
      hasOverflowY = ["auto", "overlay", "scroll"].includes(overflowYString);
      cache.hasOverflowX = hasOverflowX;
      cache.hasOverflowY = hasOverflowY;
      if (!hasOverflowX && !hasOverflowY) return false;
      if (gestureOrientation === "vertical" && !hasOverflowY) return false;
      if (gestureOrientation === "horizontal" && !hasOverflowX) return false;
      scrollWidth = node.scrollWidth;
      scrollHeight = node.scrollHeight;
      clientWidth = node.clientWidth;
      clientHeight = node.clientHeight;
      isScrollableX = scrollWidth > clientWidth;
      isScrollableY = scrollHeight > clientHeight;
      cache.isScrollableX = isScrollableX;
      cache.isScrollableY = isScrollableY;
      cache.scrollWidth = scrollWidth;
      cache.scrollHeight = scrollHeight;
      cache.clientWidth = clientWidth;
      cache.clientHeight = clientHeight;
    } else {
      isScrollableX = cache.isScrollableX;
      isScrollableY = cache.isScrollableY;
      hasOverflowX = cache.hasOverflowX;
      hasOverflowY = cache.hasOverflowY;
      scrollWidth = cache.scrollWidth;
      scrollHeight = cache.scrollHeight;
      clientWidth = cache.clientWidth;
      clientHeight = cache.clientHeight;
    }
    if (!hasOverflowX && !hasOverflowY || !isScrollableX && !isScrollableY) {
      return false;
    }
    if (gestureOrientation === "vertical" && (!hasOverflowY || !isScrollableY))
      return false;
    if (gestureOrientation === "horizontal" && (!hasOverflowX || !isScrollableX))
      return false;
    let orientation;
    if (gestureOrientation === "horizontal") {
      orientation = "x";
    } else if (gestureOrientation === "vertical") {
      orientation = "y";
    } else {
      const isScrollingX = deltaX !== 0;
      const isScrollingY = deltaY !== 0;
      if (isScrollingX && hasOverflowX && isScrollableX) {
        orientation = "x";
      }
      if (isScrollingY && hasOverflowY && isScrollableY) {
        orientation = "y";
      }
    }
    if (!orientation) return false;
    let scroll, maxScroll, delta, hasOverflow, isScrollable;
    if (orientation === "x") {
      scroll = node.scrollLeft;
      maxScroll = scrollWidth - clientWidth;
      delta = deltaX;
      hasOverflow = hasOverflowX;
      isScrollable = isScrollableX;
    } else if (orientation === "y") {
      scroll = node.scrollTop;
      maxScroll = scrollHeight - clientHeight;
      delta = deltaY;
      hasOverflow = hasOverflowY;
      isScrollable = isScrollableY;
    } else {
      return false;
    }
    const willScroll = delta > 0 ? scroll < maxScroll : scroll > 0;
    return willScroll && hasOverflow && isScrollable;
  }
  /**
   * The root element on which lenis is instanced
   */
  get rootElement() {
    return this.options.wrapper === window ? document.documentElement : this.options.wrapper;
  }
  /**
   * The limit which is the maximum scroll value
   */
  get limit() {
    if (this.options.naiveDimensions) {
      if (this.isHorizontal) {
        return this.rootElement.scrollWidth - this.rootElement.clientWidth;
      } else {
        return this.rootElement.scrollHeight - this.rootElement.clientHeight;
      }
    } else {
      return this.dimensions.limit[this.isHorizontal ? "x" : "y"];
    }
  }
  /**
   * Whether or not the scroll is horizontal
   */
  get isHorizontal() {
    return this.options.orientation === "horizontal";
  }
  /**
   * The actual scroll value
   */
  get actualScroll() {
    const wrapper = this.options.wrapper;
    return this.isHorizontal ? wrapper.scrollX ?? wrapper.scrollLeft : wrapper.scrollY ?? wrapper.scrollTop;
  }
  /**
   * The current scroll value
   */
  get scroll() {
    return this.options.infinite ? modulo(this.animatedScroll, this.limit) : this.animatedScroll;
  }
  /**
   * The progress of the scroll relative to the limit
   */
  get progress() {
    return this.limit === 0 ? 1 : this.scroll / this.limit;
  }
  /**
   * Current scroll state
   */
  get isScrolling() {
    return this._isScrolling;
  }
  set isScrolling(value) {
    if (this._isScrolling !== value) {
      this._isScrolling = value;
      this.updateClassName();
    }
  }
  /**
   * Check if lenis is stopped
   */
  get isStopped() {
    return this._isStopped;
  }
  set isStopped(value) {
    if (this._isStopped !== value) {
      this._isStopped = value;
      this.updateClassName();
    }
  }
  /**
   * Check if lenis is locked
   */
  get isLocked() {
    return this._isLocked;
  }
  set isLocked(value) {
    if (this._isLocked !== value) {
      this._isLocked = value;
      this.updateClassName();
    }
  }
  /**
   * Check if lenis is smooth scrolling
   */
  get isSmooth() {
    return this.isScrolling === "smooth";
  }
  /**
   * The class name applied to the wrapper element
   */
  get className() {
    let className = "lenis";
    if (this.options.autoToggle) className += " lenis-autoToggle";
    if (this.isStopped) className += " lenis-stopped";
    if (this.isLocked) className += " lenis-locked";
    if (this.isScrolling) className += " lenis-scrolling";
    if (this.isScrolling === "smooth") className += " lenis-smooth";
    return className;
  }
  updateClassName() {
    this.cleanUpClassName();
    this.rootElement.className = `${this.rootElement.className} ${this.className}`.trim();
  }
  cleanUpClassName() {
    this.rootElement.className = this.rootElement.className.replace(/lenis(-\w+)?/g, "").trim();
  }
};
gsapWithCSS.registerPlugin(ScrollTrigger);
let lenisInstance = null;
const customScroll = () => {
  if (lenisInstance) return;
  lenisInstance = new Lenis({
    smoothWheel: true,
    duration: 2,
    wheelMultiplier: 1
  });
  lenisInstance.on("scroll", ScrollTrigger.update);
  ScrollTrigger.scrollerProxy(document.body, {
    scrollTop(value) {
      if (arguments.length && value !== void 0) lenisInstance.scrollTo(value);
      return lenisInstance.scroll;
    },
    getBoundingClientRect() {
      return { top: 0, left: 0, width: window.innerWidth, height: window.innerHeight };
    }
  });
  ScrollTrigger.defaults({ scroller: document.body });
  function raf(time) {
    lenisInstance == null ? void 0 : lenisInstance.raf(time);
    requestAnimationFrame(raf);
  }
  requestAnimationFrame(raf);
};
customScroll();
const navLinksHover = () => {
  const LINK_SELECTOR = "[nav-link]";
  const hoverLinksHeader = () => {
    const headerMenu = document.querySelector('[data-name="navigation"]');
    const links = document.querySelectorAll(LINK_SELECTOR);
    const createWrapperLink = (link, contentLink, classWord) => {
      const wrapperLink = document.createElement("div");
      wrapperLink.classList.add(classWord);
      const words = contentLink.trim().split(" ");
      words.forEach((word, wordIndex) => {
        const wordElement = document.createElement("div");
        wordElement.classList.add("navigation-item__word");
        const chars = [...word];
        chars.forEach((char) => {
          const span = document.createElement("span");
          span.classList.add("char");
          span.textContent = char;
          wordElement.append(span);
        });
        wrapperLink.append(wordElement);
        if (wordIndex < words.length - 1) {
          const spaceElement = document.createElement("span");
          spaceElement.textContent = " ";
          wrapperLink.append(spaceElement);
        }
      });
      link.append(wrapperLink);
    };
    links.forEach((link) => {
      const contentLink = link.textContent || "";
      link.textContent = "";
      createWrapperLink(link, contentLink, "navigation-item__wrapper-word");
      createWrapperLink(link, contentLink, "navigation-item__wrapper-word-double");
    });
    links.forEach((link) => {
      const wrapperWord = link.querySelector(".navigation-item__wrapper-word");
      const wrapperWordDouble = link.querySelector(".navigation-item__wrapper-word-double");
      if (wrapperWordDouble) {
        link.style.minWidth = `${Math.ceil(wrapperWordDouble.scrollWidth) + 4}px`;
      }
      if (!wrapperWord || !wrapperWordDouble) return;
      const charsWord = wrapperWord.querySelectorAll(".char");
      const charsWordDouble = wrapperWordDouble.querySelectorAll(".char");
      charsWordDouble.forEach((char) => {
        char.style.transform = "translate(0, 115%)";
      });
      charsWord.forEach((char) => {
        char.style.transform = "translateX(0, 0)";
      });
      link.addEventListener("mouseover", () => {
        link.classList.add(CLASSES.ACTIVE);
        charsWord.forEach((char, index) => {
          setTimeout(() => {
            char.style.transform = "translate(0, -125%)";
          }, index * 30);
        });
        charsWordDouble.forEach((char, index) => {
          setTimeout(() => {
            char.style.transform = "translateX(0)";
          }, index * 30);
        });
      });
      link.addEventListener("mouseout", () => {
        link.classList.remove(CLASSES.ACTIVE);
        charsWord.forEach((char, index) => {
          setTimeout(() => {
            char.style.transform = "translate(0, 0)";
          }, index * 30);
        });
        charsWordDouble.forEach((char, index) => {
          setTimeout(() => {
            char.style.transform = "translate(0, 125%)";
          }, index * 30);
        });
      });
    });
    const observer = new MutationObserver((mutationsList) => {
      mutationsList.forEach((mutation) => {
        if (mutation.type === "attributes" && mutation.attributeName === "class") {
          const elementMutationTarget = mutation.target;
          if (elementMutationTarget && elementMutationTarget.classList.contains("js--active")) {
            links.forEach((link, linkIndex) => {
              const wrapperWord = link.querySelector(".navigation-item__wrapper-word");
              const wrapperWordDouble = link.querySelector(".navigation-item__wrapper-word-double");
              if (!wrapperWord || !wrapperWordDouble) return;
              const charsWord = wrapperWord.querySelectorAll(".char");
              const charsWordDouble = wrapperWordDouble.querySelectorAll(".char");
              setTimeout(() => {
                charsWord.forEach((char, index) => {
                  setTimeout(() => {
                    char.style.transform = "translate(0, -125%)";
                  }, index * 50);
                });
                charsWordDouble.forEach((char, index) => {
                  setTimeout(() => {
                    char.style.transform = "translateY(0)";
                  }, index * 50);
                });
              }, linkIndex * 200);
            });
          } else {
            links.forEach((link, linkIndex) => {
              const wrapperWord = link.querySelector(".navigation-item__wrapper-word");
              const wrapperWordDouble = link.querySelector(".navigation-item__wrapper-word-double");
              if (!wrapperWord || !wrapperWordDouble) return;
              const charsWord = wrapperWord.querySelectorAll(".char");
              const charsWordDouble = wrapperWordDouble.querySelectorAll(".char");
              setTimeout(() => {
                charsWord.forEach((char) => {
                  char.style.transition = "none";
                  char.style.transform = "translate(0, 0)";
                });
                charsWordDouble.forEach((char) => {
                  char.style.transition = "none";
                  char.style.transform = "translate(0, 125%)";
                });
                setTimeout(() => {
                  charsWord.forEach((char) => {
                    char.style.transition = "transform 0.3s ease";
                  });
                  charsWordDouble.forEach((char) => {
                    char.style.transition = "transform 0.3s ease";
                  });
                }, 10);
              }, linkIndex * 10);
            });
          }
        }
      });
    });
    const config = { attributes: true };
    if (headerMenu) {
      observer.observe(headerMenu, config);
    }
  };
  hoverLinksHeader();
};
navLinksHover();
const innerHoverTrigger = () => {
  const hoverElements = document.querySelectorAll('[data-role="inner-hover-trigger"]');
  if (hoverElements.length === 0) return;
  const isMobile = () => window.innerWidth <= 767;
  const pauseVideo = (video) => {
    if (!video.paused) {
      video.pause();
    }
  };
  const playVideo = (video) => {
    if (video.paused) {
      video.play().catch((error) => {
        console.warn("Unable to play video:", error);
      });
    }
  };
  const handleMouseEnter = (e) => {
    if (isMobile()) return;
    const element = e.currentTarget;
    const video = element.querySelector("video");
    if (video) {
      playVideo(video);
    }
  };
  const handleMouseLeave = (e) => {
    if (isMobile()) return;
    const element = e.currentTarget;
    const video = element.querySelector("video");
    if (video) {
      pauseVideo(video);
    }
  };
  const initMobileVideo = (video) => {
    if (isMobile()) {
      video.setAttribute("autoplay", "true");
      video.setAttribute("muted", "true");
      video.setAttribute("playsinline", "true");
      playVideo(video);
    }
  };
  const initDesktopVideo = (video) => {
    if (!isMobile()) {
      video.removeAttribute("autoplay");
      pauseVideo(video);
    }
  };
  const handleResize = () => {
    hoverElements.forEach((element) => {
      const video = element.querySelector("video");
      if (video) {
        if (isMobile()) {
          initMobileVideo(video);
        } else {
          initDesktopVideo(video);
        }
      }
    });
  };
  hoverElements.forEach((element) => {
    const video = element.querySelector("video");
    if (video) {
      if (isMobile()) {
        initMobileVideo(video);
      } else {
        element.addEventListener("mouseenter", handleMouseEnter);
        element.addEventListener("mouseleave", handleMouseLeave);
        initDesktopVideo(video);
      }
    }
  });
  window.addEventListener("resize", handleResize);
  return () => {
    hoverElements.forEach((element) => {
      element.removeEventListener("mouseenter", handleMouseEnter);
      element.removeEventListener("mouseleave", handleMouseLeave);
    });
    window.removeEventListener("resize", handleResize);
  };
};
innerHoverTrigger();
const pageTransition = () => {
  const overlay = document.querySelector(".page-transition");
  const mainContent = document.querySelector('[data-role="main"]');
  if (!overlay) return;
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  let isTransitioning = false;
  let transitionTimeout = null;
  const safetyRestore = () => {
    if (transitionTimeout) {
      clearTimeout(transitionTimeout);
      transitionTimeout = null;
    }
    if (mainContent) {
      mainContent.style.opacity = "1";
    }
    overlay.style.visibility = "hidden";
    overlay.style.pointerEvents = "none";
    overlay.style.opacity = "0";
    isTransitioning = false;
  };
  const startSafetyTimeout = () => {
    if (transitionTimeout) {
      clearTimeout(transitionTimeout);
    }
    transitionTimeout = setTimeout(safetyRestore, 3e3);
  };
  const playTransition = () => {
    return new Promise((resolve) => {
      if (isTransitioning) {
        resolve();
        return;
      }
      isTransitioning = true;
      gsapWithCSS.killTweensOf([overlay, mainContent]);
      gsapWithCSS.set(overlay, {
        opacity: 0
      });
      overlay.style.visibility = "visible";
      overlay.style.pointerEvents = "auto";
      const tl = gsapWithCSS.timeline({
        onComplete: () => {
          isTransitioning = false;
          resolve();
        }
      });
      if (mainContent) {
        tl.to(
          mainContent,
          {
            duration: 0.1,
            opacity: 0,
            ease: "power2.out"
          },
          0
        );
      }
      tl.to(
        overlay,
        {
          duration: 1.1,
          opacity: 1,
          ease: "power2.inOut"
        },
        0.05
      );
      startSafetyTimeout();
    });
  };
  const playExitTransition = () => {
    return new Promise((resolve) => {
      if (isTransitioning) {
        resolve();
        return;
      }
      isTransitioning = true;
      gsapWithCSS.killTweensOf([overlay, mainContent]);
      const tl = gsapWithCSS.timeline({
        onComplete: () => {
          safetyRestore();
          resolve();
        }
      });
      tl.to(
        overlay,
        {
          duration: 0.8,
          opacity: 0,
          ease: "power2.inOut"
        },
        0
      );
      if (mainContent) {
        tl.to(
          mainContent,
          {
            duration: 0.3,
            opacity: 1,
            ease: "power2.out"
          },
          0.2
        );
      }
      startSafetyTimeout();
    });
  };
  const navigateWithTransition = (url) => {
    playTransition().then(() => {
      setTimeout(() => {
        window.location.href = url;
      }, 100);
    }).catch(() => {
      window.location.href = url;
    });
  };
  const isSamePageAnchor = (href) => {
    if (!href) return false;
    if (href.startsWith("#") || href === `${window.location.pathname}#` || href.startsWith(`${window.location.pathname}#`)) {
      return true;
    }
    try {
      const url = new URL(href, window.location.origin);
      return url.pathname === window.location.pathname && url.hash !== "";
    } catch {
      return href.startsWith("#");
    }
  };
  const isValidLink = (href) => {
    if (!href) return false;
    if (isSamePageAnchor(href)) return false;
    if (href.startsWith("http") && !href.includes(window.location.hostname)) return false;
    if (href.startsWith("mailto:") || href.startsWith("tel:") || href.startsWith("javascript:")) return false;
    if (href.includes("/download/") || href.match(/\.(pdf|doc|docx|xls|xlsx|zip)$/i)) return false;
    return true;
  };
  const handleLinkClick = (e) => {
    if (isTransitioning) {
      e.preventDefault();
      return;
    }
    const target = e.target;
    const link = target.closest("a[href]");
    if (!link) return;
    const href = link.getAttribute("href");
    if (!href || !isValidLink(href)) return;
    e.preventDefault();
    navigateWithTransition(href);
  };
  const handlePopState = () => {
    if (isMobile) {
      safetyRestore();
      return;
    }
    if (isTransitioning) {
      safetyRestore();
      return;
    }
    playExitTransition().catch(safetyRestore);
  };
  const handleVisibilityChange = () => {
    if (document.visibilityState === "visible") {
      setTimeout(safetyRestore, 100);
    }
  };
  const init = () => {
    document.addEventListener("click", handleLinkClick);
    window.addEventListener("popstate", handlePopState);
    document.addEventListener("visibilitychange", handleVisibilityChange);
    safetyRestore();
  };
  const destroy = () => {
    document.removeEventListener("click", handleLinkClick);
    window.removeEventListener("popstate", handlePopState);
    document.removeEventListener("visibilitychange", handleVisibilityChange);
    if (transitionTimeout) {
      clearTimeout(transitionTimeout);
    }
    safetyRestore();
  };
  window.addEventListener("load", () => {
    setTimeout(() => {
      if (!isMobile) {
        playExitTransition().catch(safetyRestore);
      } else {
        safetyRestore();
      }
    }, 100);
  });
  setTimeout(safetyRestore, 5e3);
  init();
  return {
    playTransition,
    navigateWithTransition,
    destroy,
    safetyRestore
  };
};
pageTransition();
const optimizeVideos = () => {
  const videos = document.querySelectorAll("video");
  videos.forEach((video) => {
    video.preload = "metadata";
    if (video.classList.contains("background-video")) {
      video.muted = true;
      video.loop = true;
      video.playsInline = true;
      if ("requestVideoFrameCallback" in video) {
        let lastTime = performance.now();
        const onVideoFrame = (now) => {
          const delta = now - lastTime;
          if (delta > 50) {
            video.playbackRate = 0.5;
          } else {
            video.playbackRate = 1;
          }
          lastTime = now;
          video.requestVideoFrameCallback(onVideoFrame);
        };
        video.requestVideoFrameCallback(onVideoFrame);
      }
    }
    if (!video.autoplay) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              video.load();
              observer.unobserve(video);
            }
          });
        },
        { threshold: 0.1 }
      );
      observer.observe(video);
    }
  });
};
const checkPerformance = () => {
  performance.now();
  function checkFPS() {
    performance.now();
    requestAnimationFrame(checkFPS);
  }
  requestAnimationFrame(checkFPS);
};
optimizeVideos();
checkPerformance();
