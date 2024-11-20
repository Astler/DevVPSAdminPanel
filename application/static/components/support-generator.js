window.SupportGenerator = function() {
  const [message, setMessage] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [history, setHistory] = React.useState(() => {
    const saved = localStorage.getItem('supportHistory');
    return saved ? JSON.parse(saved) : [];
  });

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
      const newHistory = [...history, data.message].slice(-3);
      setHistory(newHistory);
      localStorage.setItem('supportHistory', JSON.stringify(newHistory));
    } catch (error) {
      console.error('Error:', error);
      setMessage('Произошла ошибка при генерации сообщения. Пожалуйста, попробуйте еще раз.');
    } finally {
      setLoading(false);
    }
  };

  return React.createElement('div', {
    className: 'w-full max-w-2xl mx-auto bg-surface p-8 rounded-xl shadow-lg'
  }, [
    React.createElement('h2', {
      className: 'text-2xl font-medium text-center mb-8',
      key: 'title'
    }, 'Поддержка Милов 💝'),
    React.createElement('div', {
      className: 'space-y-6',
      key: 'content'
    }, [
      React.createElement('div', {
        className: 'flex justify-center',
        key: 'button-container'
      },
        React.createElement('button', {
          onClick: generateMessage,
          disabled: loading,
          className: 'px-8 py-4 bg-primary text-on-primary rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-all duration-300 flex items-center gap-2 font-medium',
          key: 'generate-button'
        }, loading ? '✨ Генерация...' : '✨ Создать слова поддержки')
      ),
      message && React.createElement('div', {
        className: 'p-6 bg-surface-variant rounded-lg border border-outline shadow-lg transition-all duration-300 hover:shadow-xl',
        key: 'message-container'
      },
        React.createElement('p', {
          className: 'text-lg leading-relaxed whitespace-pre-wrap',
          key: 'message-text'
        }, message)
      ),
      history.length > 0 && React.createElement('div', {
        className: 'mt-8',
        key: 'history'
      }, [
        React.createElement('h3', {
          className: 'text-lg font-medium mb-4 text-center text-on-surface/70',
          key: 'history-title'
        }, 'История'),
        ...history.map((msg, idx) =>
          React.createElement('div', {
            className: 'p-4 bg-surface-variant rounded-lg border border-outline/50 shadow mb-4 opacity-70 hover:opacity-100 transition-opacity duration-300',
            key: `history-${idx}`
          },
            React.createElement('p', {
              className: 'text-base leading-relaxed whitespace-pre-wrap',
              key: `history-text-${idx}`
            }, msg)
          )
        )
      ])
    ])
  ]);
};