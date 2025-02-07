const getCookie = (name) => {
    if (document?.cookie === '')
      return null;

    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === `${name}=`)
          return decodeURIComponent(cookie.substring(name.length + 1));
    }
    return null;
};

export const csrftoken = getCookie('csrftoken');
