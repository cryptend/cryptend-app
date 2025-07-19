let form = document.querySelector('form[method="post"]');
if (form) {
  form.addEventListener('submit', function(event) {
    event.preventDefault();
    let btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    let loading = btn.querySelector('.loading');
    if (loading) {
      btn.querySelector('span').remove();
      loading.classList.remove('hidden');
    }
    form.submit();
  });
}

let btn = document.getElementById('copy-btn');
if (btn) {
  btn.addEventListener('click', function() {
    let text = document.getElementById('output').innerText;
    navigator.clipboard.writeText(text).then(() => {
      let btnText = btn.innerText;
      btn.innerText = 'Copied';
      setTimeout(() => {
        btn.innerText = btnText;
      }, 1000);
    });
  });
}