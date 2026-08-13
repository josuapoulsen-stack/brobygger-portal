using System.Collections.Concurrent;
using System.Threading.Channels;

namespace BrobyggerPortal.Api.Services;

// In-memory event-broker til Server-Sent Events (SSE). Én instans (singleton);
// hver SSE-forbindelse abonnerer og får sin egen kanal. Ved multi-instans på Azure
// erstattes fan-out med Postgres LISTEN/NOTIFY (se IMPLEMENTERINGSPLAN 3.2).
public class EventBroker
{
    private readonly ConcurrentDictionary<Guid, Channel<string>> _subs = new();

    public (Guid Id, ChannelReader<string> Reader) Subscribe()
    {
        var id = Guid.NewGuid();
        var ch = Channel.CreateUnbounded<string>();
        _subs[id] = ch;
        return (id, ch.Reader);
    }

    public void Unsubscribe(Guid id)
    {
        if (_subs.TryRemove(id, out var ch)) ch.Writer.TryComplete();
    }

    public void Publish(string data)
    {
        foreach (var ch in _subs.Values) ch.Writer.TryWrite(data);
    }
}
