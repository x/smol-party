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

var jsConfetti = null;

// Use this for testing the confetti.
function launchConfetti(emojisString, confettiAmount) {
    if (jsConfetti === null) {
      jsConfetti = new JSConfetti();
    }
    jsConfetti.addConfetti({
        "emojis": Array.from(emojisString),
        "confettiNumber": confettiAmount,
    });
}