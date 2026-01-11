import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Icon from '@/components/ui/icon';

interface FileItem {
  id: string;
  title: string;
  type: string;
  thumbnail: string;
  formats: string[];
  tags: string[];
}

const mockFiles: FileItem[] = [
  {
    id: '1',
    title: 'Abstract Gradient Background',
    type: 'Background',
    thumbnail: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&h=300&fit=crop',
    formats: ['PSD', 'PNG', 'SVG'],
    tags: ['gradient', 'abstract', 'colorful']
  },
  {
    id: '2',
    title: 'Modern UI Kit Design',
    type: 'UI Kit',
    thumbnail: 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=300&fit=crop',
    formats: ['PSD', 'PNG', 'GIF'],
    tags: ['ui', 'modern', 'interface']
  },
  {
    id: '3',
    title: 'Social Media Templates',
    type: 'Template',
    thumbnail: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400&h=300&fit=crop',
    formats: ['PSD', 'PNG'],
    tags: ['social', 'instagram', 'post']
  },
  {
    id: '4',
    title: 'Animated Logo Pack',
    type: 'Logo',
    thumbnail: 'https://images.unsplash.com/photo-1626785774573-4b799315345d?w=400&h=300&fit=crop',
    formats: ['GIF', 'PNG', 'SVG'],
    tags: ['logo', 'animation', 'branding']
  },
  {
    id: '5',
    title: 'Vector Icons Collection',
    type: 'Icons',
    thumbnail: 'https://images.unsplash.com/photo-1618556450994-a6a128ef0d9d?w=400&h=300&fit=crop',
    formats: ['SVG', 'PNG'],
    tags: ['icons', 'vector', 'flat']
  },
  {
    id: '6',
    title: 'Business Card Mockup',
    type: 'Mockup',
    thumbnail: 'https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=400&h=300&fit=crop',
    formats: ['PSD', 'PNG'],
    tags: ['mockup', 'business', 'card']
  }
];

const mockHistory: FileItem[] = [
  {
    id: 'h1',
    title: 'Abstract Gradient Background',
    type: 'Background',
    thumbnail: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&h=300&fit=crop',
    formats: ['PNG'],
    tags: ['gradient', 'abstract']
  },
  {
    id: 'h2',
    title: 'Modern UI Kit Design',
    type: 'UI Kit',
    thumbnail: 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=300&fit=crop',
    formats: ['PSD'],
    tags: ['ui', 'modern']
  }
];

export default function Index() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);
  const [selectedFormat, setSelectedFormat] = useState<string>('');

  const filteredFiles = mockFiles.filter(file =>
    file.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    file.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleDownload = () => {
    if (selectedFile && selectedFormat) {
      alert(`Скачивается ${selectedFile.title} в формате ${selectedFormat}`);
      setSelectedFile(null);
      setSelectedFormat('');
    }
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
            <p className="text-sm text-muted-foreground">Премиум-файлы бесплатно</p>
          </div>
        </div>

        <Tabs defaultValue="search" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="search" className="gap-2">
              <Icon name="Search" size={16} />
              Поиск
            </TabsTrigger>
            <TabsTrigger value="history" className="gap-2">
              <Icon name="Clock" size={16} />
              История
            </TabsTrigger>
          </TabsList>

          <TabsContent value="search" className="space-y-6">
            <div className="relative">
              <Icon name="Search" size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Поиск по названию или тегам..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 h-12 text-base"
              />
            </div>

            <div className="grid gap-4">
              {filteredFiles.map((file) => (
                <Card key={file.id} className="overflow-hidden hover:border-primary transition-all cursor-pointer group" onClick={() => setSelectedFile(file)}>
                  <CardContent className="p-0">
                    <div className="flex gap-4 p-4">
                      <div className="relative w-32 h-24 rounded-lg overflow-hidden flex-shrink-0 bg-muted">
                        <img src={file.thumbnail} alt={file.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                        <div className="absolute top-2 right-2">
                          <Badge variant="secondary" className="text-xs font-medium">
                            {file.type}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-foreground mb-2 truncate">{file.title}</h3>
                        <div className="flex flex-wrap gap-1.5 mb-2">
                          {file.tags.map((tag) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              #{tag}
                            </Badge>
                          ))}
                        </div>
                        <div className="flex gap-2">
                          {file.formats.map((format) => (
                            <Badge key={format} className="text-xs">
                              {format}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div className="flex items-center">
                        <Icon name="ChevronRight" size={20} className="text-muted-foreground group-hover:text-primary transition-colors" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
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
                  <Card key={file.id} className="overflow-hidden">
                    <CardContent className="p-0">
                      <div className="flex gap-4 p-4">
                        <div className="relative w-32 h-24 rounded-lg overflow-hidden flex-shrink-0 bg-muted">
                          <img src={file.thumbnail} alt={file.title} className="w-full h-full object-cover" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-foreground mb-2 truncate">{file.title}</h3>
                          <div className="flex flex-wrap gap-1.5 mb-2">
                            {file.tags.map((tag) => (
                              <Badge key={tag} variant="outline" className="text-xs">
                                #{tag}
                              </Badge>
                            ))}
                          </div>
                          <Badge className="text-xs">{file.formats[0]}</Badge>
                        </div>
                        <div className="flex items-center">
                          <Button variant="ghost" size="icon">
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

      {selectedFile && (
        <div className="fixed inset-0 bg-black/80 flex items-end sm:items-center justify-center z-50 animate-in fade-in duration-200" onClick={() => setSelectedFile(null)}>
          <Card className="w-full max-w-md m-0 sm:m-4 rounded-t-3xl sm:rounded-2xl animate-in slide-in-from-bottom duration-300" onClick={(e) => e.stopPropagation()}>
            <CardContent className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-xl font-bold text-foreground mb-1">{selectedFile.title}</h2>
                  <Badge variant="secondary">{selectedFile.type}</Badge>
                </div>
                <Button variant="ghost" size="icon" onClick={() => setSelectedFile(null)}>
                  <Icon name="X" size={20} />
                </Button>
              </div>

              <div className="relative w-full h-48 rounded-xl overflow-hidden mb-4 bg-muted">
                <img src={selectedFile.thumbnail} alt={selectedFile.title} className="w-full h-full object-cover" />
              </div>

              <div className="mb-4">
                <p className="text-sm font-medium text-foreground mb-3">Выберите формат:</p>
                <div className="grid grid-cols-4 gap-2">
                  {selectedFile.formats.map((format) => (
                    <Button
                      key={format}
                      variant={selectedFormat === format ? 'default' : 'outline'}
                      className="h-12"
                      onClick={() => setSelectedFormat(format)}
                    >
                      {format}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="flex flex-wrap gap-1.5 mb-6">
                {selectedFile.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    #{tag}
                  </Badge>
                ))}
              </div>

              <Button
                className="w-full h-12 text-base gap-2"
                disabled={!selectedFormat}
                onClick={handleDownload}
              >
                <Icon name="Download" size={20} />
                Скачать {selectedFormat}
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
