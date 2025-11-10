// Carousel Banner Script
document.addEventListener("DOMContentLoaded", () => {
  const slides = document.querySelectorAll(".carousel-slide");
  const dotsContainer = document.querySelector(".carousel-dots");
  let current = 0;
  const total = slides.length;

  // Tạo chấm nhỏ tương ứng với số slide
  slides.forEach((_, i) => {
    const dot = document.createElement("span");
    if (i === 0) dot.classList.add("active");
    dot.addEventListener("click", () => showSlide(i));
    dotsContainer.appendChild(dot);
  });

  const dots = document.querySelectorAll(".carousel-dots span");

  function showSlide(index) {
    slides.forEach(s => s.classList.remove("active"));
    dots.forEach(d => d.classList.remove("active"));
    slides[index].classList.add("active");
    dots[index].classList.add("active");
    current = index;
  }

  // Nút next/prev
  document.querySelector(".next").addEventListener("click", () => {
    showSlide((current + 1) % total);
  });
  document.querySelector(".prev").addEventListener("click", () => {
    showSlide((current - 1 + total) % total);
  });

  // Tự động chạy
  setInterval(() => {
    showSlide((current + 1) % total);
  }, 5000); // 5s
});
