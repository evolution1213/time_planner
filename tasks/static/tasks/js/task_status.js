function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    document.cookie.split(';').forEach((cookie) => {
      const trimmed = cookie.trim();
      if (trimmed.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
      }
    });
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function updateTaskCardVisual(checkbox) {
  const card = checkbox.closest('.card');
  if (!card) {
    return;
  }

  card.classList.toggle('done-task', checkbox.checked);
}

function handleTaskToggle(event) {
  const checkbox = event.currentTarget;
  const taskId = checkbox.dataset.taskId;
  if (!taskId) {
    return;
  }

  const done = checkbox.checked;
  const card = checkbox.closest('.card');

  checkbox.disabled = true;

  fetch(`/task/${taskId}/toggle/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrftoken,
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: new URLSearchParams({ done: done ? 'true' : 'false' }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error('Server error');
      }
      return response.json();
    })
    .then((data) => {
      if (!data.success) {
        throw new Error(data.error || 'Unable to update task status.');
      }
      updateTaskCardVisual(checkbox);
    })
    .catch((error) => {
      console.error(error);
      checkbox.checked = !done;
      if (card) {
        card.classList.toggle('done-task', checkbox.checked);
      }
    })
    .finally(() => {
      checkbox.disabled = false;
    });
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.task-done-toggle').forEach((checkbox) => {
    checkbox.addEventListener('change', handleTaskToggle);
    updateTaskCardVisual(checkbox);
  });
});
