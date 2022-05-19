function shareEvent(title, text, url) {
  if (navigator.share) {
    navigator
      .share({
        title: title,
        text: text,
        url: url,
      })
      .then(() => console.log("Successful share"))
      .catch((error) => console.log("Error sharing", error));
  }
}

const jsConfetti = new JSConfetti({ canvas })
jsConfetti.addConfetti()