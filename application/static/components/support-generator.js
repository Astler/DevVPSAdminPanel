window.SupportGenerator = function() {
  const [message, setMessage] = React.useState('');
  const [loading, setLoading] = React.useState(false);

  const generateMessage = async () => {
    setLoading(true);
    try {
      const response = await fetch('/mi_support/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      setMessage(data.message);
    } catch (error) {
      console.error('Error:', error);
      setMessage('Произошла ошибка при генерации сообщения. Пожалуйста, попробуйте еще раз.');
    } finally {
      setLoading(false);
    }
  };

  return React.createElement('div', {
    className: 'w-full max-w-2xl mx-auto bg-surface p-6 rounded-lg shadow'
  }, [
    React.createElement('h2', {
      className: 'text-2xl font-bold text-center mb-6',
      key: 'title'
    }, 'Генератор слов поддержки 💝'),
    React.createElement('div', {
      className: 'space-y-4',
      key: 'content'
    }, [
      React.createElement('div', {
        className: 'flex justify-center',
        key: 'button-container'
      },
        React.createElement('button', {
          onClick: generateMessage,
          disabled: loading,
          className: 'px-6 py-3 bg-primary text-on-primary rounded-full hover:bg-primary/90 disabled:opacity-50 transition-all duration-300 transform hover:scale-105',
          key: 'generate-button'
        }, loading ? '✨ Генерация...' : '✨ Создать слова поддержки')
      ),
      message && React.createElement('div', {
        className: 'mt-6 p-6 bg-surface-variant rounded-lg border border-outline shadow-lg',
        key: 'message-container'
      },
        React.createElement('p', {
          className: 'text-lg leading-relaxed whitespace-pre-wrap',
          key: 'message-text'
        }, message)
      )
    ])
  ]);
};