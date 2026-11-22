/***************** Scroll-triggered fade-ins ******************/
// Adding class wp1–wp6 to an element fades it in when it scrolls into view.
// `offset` is how far down the viewport the element's top must reach (like the old Waypoints offset).

(function () {
	var effects = {
		wp1: ['fadeInLeft', '75%'],
		wp2: ['fadeInUp', '75%'],
		wp3: ['fadeInDown', '55%'],
		wp4: ['fadeInDown', '75%'],
		wp5: ['fadeInUp', '75%'],
		wp6: ['fadeInDown', '75%']
	};

	Object.keys(effects).forEach(function (cls) {
		var anim = effects[cls][0];
		var offset = effects[cls][1];
		var els = document.querySelectorAll('.' + cls);
		if (!els.length) return;

		var reveal = function (el) { el.classList.add('animated', anim); };

		if (!('IntersectionObserver' in window)) {
			els.forEach(reveal);
			return;
		}

		var bottomMargin = '-' + (100 - parseFloat(offset)) + '%';
		var io = new IntersectionObserver(function (entries) {
			entries.forEach(function (entry) {
				// Reveal once the element enters the trigger zone or has already been scrolled past.
				if (entry.isIntersecting || entry.boundingClientRect.top < 0) {
					reveal(entry.target);
					io.unobserve(entry.target);
				}
			});
		}, { rootMargin: '0px 0px ' + bottomMargin + ' 0px' });

		els.forEach(function (el) { io.observe(el); });
	});
})();
