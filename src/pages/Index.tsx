import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Icon from '@/components/ui/icon';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface DownloadedFile {
  id: string;
  title: string;
  url: string;
  format: string;
  downloadedAt: string;
  thumbnail?: string;
}

const mockHistory: DownloadedFile[] = [
  {
    id: '1',
    title: 'abstract-gradient-background.psd',
    url: 'https://freepik.com/premium/abstract-gradient-12345',
    format: 'PSD',
    downloadedAt: '2 часа назад',
    thumbnail: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&h=300&fit=crop'
  },
  {
    id: '2',
    title: 'modern-ui-kit-design.png',
    url: 'https://freepik.com/premium/ui-kit-67890',
    format: 'PNG',
    downloadedAt: 'вчера',
    thumbnail: 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=300&fit=crop'
  }
];

export default function Index() {
  const [freepikUrl, setFreepikUrl] = useState('');
  const [selectedFormat, setSelectedFormat] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showFormatSelection, setShowFormatSelection] = useState(false);

  const availableFormats = ['PSD', 'PNG', 'GIF', 'SVG', 'JPG', 'AI', 'EPS'];

  const isValidFreepikUrl = (url: string) => {
    return url.includes('freepik.com') || url.includes('flaticon.com');
  };

  const handleUrlChange = (value: string) => {
    setFreepikUrl(value);
    setError('');
    setShowFormatSelection(false);
  };

  const handleCheckUrl = () => {
    if (!freepikUrl.trim()) {
      setError('Вставьте ссылку на файл');
      return;
    }

    if (!isValidFreepikUrl(freepikUrl)) {
      setError('Это не ссылка с Freepik или Flaticon');
      return;
    }

    setShowFormatSelection(true);
    setError('');
  };

  const handleDownload = async () => {
    if (!selectedFormat) {
      setError('Выберите формат');
      return;
    }

    setIsLoading(true);
    
    setTimeout(() => {
      setIsLoading(false);
      setFreepikUrl('');
      setSelectedFormat('');
      setShowFormatSelection(false);
      alert(`Файл скачивается в формате ${selectedFormat}!`);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container max-w-4xl mx-auto px-4 py-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-2xl bg-primary flex items-center justify-center">
            <Icon name="Download" size={24} className="text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground">Freepik Bot</h1>
            <p className="text-sm text-muted-foreground">Скачивай премиум-файлы бесплатно</p>
          </div>
        </div>

        <Tabs defaultValue="download" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="download" className="gap-2">
              <Icon name="Link" size={16} />
              Скачать
            </TabsTrigger>
            <TabsTrigger value="history" className="gap-2">
              <Icon name="Clock" size={16} />
              История
            </TabsTrigger>
          </TabsList>

          <TabsContent value="download" className="space-y-4">
            <Card>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-foreground mb-2 block">
                      Ссылка на файл с Freepik
                    </label>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Icon name="Link" size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                        <Input
                          type="text"
                          placeholder="https://freepik.com/premium/..."
                          value={freepikUrl}
                          onChange={(e) => handleUrlChange(e.target.value)}
                          className="pl-10 h-12 text-base"
                          disabled={isLoading}
                        />
                      </div>
                      <Button 
                        onClick={handleCheckUrl} 
                        className="h-12 px-6"
                        disabled={isLoading || !freepikUrl.trim()}
                      >
                        <Icon name="Search" size={20} />
                      </Button>
                    </div>
                  </div>

                  {error && (
                    <Alert variant="destructive">
                      <Icon name="AlertCircle" size={16} />
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}

                  {showFormatSelection && (
                    <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
                      <div className="p-4 rounded-lg bg-muted/50 border border-border">
                        <div className="flex items-start gap-3 mb-3">
                          <Icon name="CheckCircle2" size={20} className="text-primary mt-0.5" />
                          <div>
                            <p className="font-medium text-foreground">Файл найден!</p>
                            <p className="text-sm text-muted-foreground">Выберите формат для скачивания</p>
                          </div>
                        </div>
                      </div>

                      <div>
                        <label className="text-sm font-medium text-foreground mb-3 block">
                          Доступные форматы:
                        </label>
                        <div className="grid grid-cols-4 gap-2">
                          {availableFormats.map((format) => (
                            <Button
                              key={format}
                              variant={selectedFormat === format ? 'default' : 'outline'}
                              className="h-14 text-base font-semibold"
                              onClick={() => setSelectedFormat(format)}
                              disabled={isLoading}
                            >
                              {format}
                            </Button>
                          ))}
                        </div>
                      </div>

                      <Button
                        className="w-full h-14 text-base gap-2"
                        disabled={!selectedFormat || isLoading}
                        onClick={handleDownload}
                      >
                        {isLoading ? (
                          <>
                            <Icon name="Loader2" size={20} className="animate-spin" />
                            Скачивание...
                          </>
                        ) : (
                          <>
                            <Icon name="Download" size={20} />
                            Скачать {selectedFormat}
                          </>
                        )}
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-muted/30">
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <Icon name="Info" size={20} className="text-primary mt-0.5 flex-shrink-0" />
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <p className="font-medium text-foreground">Как использовать:</p>
                    <ol className="list-decimal list-inside space-y-1 ml-2">
                      <li>Найди нужный файл на freepik.com или flaticon.com</li>
                      <li>Скопируй ссылку на файл</li>
                      <li>Вставь ссылку в поле выше</li>
                      <li>Выбери формат и скачай бесплатно</li>
                    </ol>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history" className="space-y-4">
            {mockHistory.length === 0 ? (
              <Card className="p-12">
                <div className="flex flex-col items-center justify-center text-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center">
                    <Icon name="Clock" size={32} className="text-muted-foreground" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground mb-1">История пуста</h3>
                    <p className="text-sm text-muted-foreground">Скачанные файлы появятся здесь</p>
                  </div>
                </div>
              </Card>
            ) : (
              <div className="grid gap-4">
                {mockHistory.map((file) => (
                  <Card key={file.id} className="overflow-hidden hover:border-primary transition-all group">
                    <CardContent className="p-0">
                      <div className="flex gap-4 p-4">
                        {file.thumbnail && (
                          <div className="relative w-24 h-24 rounded-lg overflow-hidden flex-shrink-0 bg-muted">
                            <img src={file.thumbnail} alt={file.title} className="w-full h-full object-cover" />
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-foreground mb-1 truncate">{file.title}</h3>
                          <p className="text-xs text-muted-foreground mb-2 truncate">{file.url}</p>
                          <div className="flex items-center gap-2">
                            <Badge className="text-xs">{file.format}</Badge>
                            <span className="text-xs text-muted-foreground">{file.downloadedAt}</span>
                          </div>
                        </div>
                        <div className="flex items-center">
                          <Button variant="ghost" size="icon" className="group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                            <Icon name="Download" size={20} />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
