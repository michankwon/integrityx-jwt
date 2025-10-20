'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle 
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Copy, 
  Check, 
  Shield, 
  Anchor, 
  FileSignature, 
  Code, 
  Eye,
  Calendar,
  Hash,
  Key,
  ExternalLink
} from 'lucide-react';
import toast from 'react-hot-toast';

// Copy Button Component
interface CopyButtonProps {
  readonly text: string;
  readonly fieldName: string;
  readonly label: string;
  readonly copiedFields: Set<string>;
  readonly onCopy: (text: string, fieldName: string) => void;
}

function CopyButton({ text, fieldName, label, copiedFields, onCopy }: CopyButtonProps) {
  const isCopied = copiedFields.has(fieldName);
  
  return (
    <Button
      variant="outline"
      size="sm"
      onClick={() => onCopy(text, fieldName)}
      className="ml-2"
    >
      {isCopied ? (
        <>
          <Check className="h-3 w-3 mr-1" />
          Copied
        </>
      ) : (
        <>
          <Copy className="h-3 w-3 mr-1" />
          Copy {label}
        </>
      )}
    </Button>
  );
}

// Collapsible Section Component
interface CollapsibleSectionProps {
  readonly id: string;
  readonly title: string;
  readonly icon: React.ComponentType<{ className?: string }>;
  readonly children: React.ReactNode;
  readonly defaultExpanded?: boolean;
  readonly expandedSections: Set<string>;
  readonly onToggle: (sectionId: string) => void;
}

function CollapsibleSection({ 
  id, 
  title, 
  icon: Icon, 
  children, 
  defaultExpanded = false,
  expandedSections,
  onToggle
}: CollapsibleSectionProps) {
  const isExpanded = expandedSections.has(id);
    
  useEffect(() => {
    if (defaultExpanded && !expandedSections.has(id)) {
      onToggle(id);
    }
  }, [id, defaultExpanded, expandedSections, onToggle]);

  return (
    <Card className="mb-4">
      <CardHeader 
        className="cursor-pointer hover:bg-muted/50 transition-colors"
        onClick={() => onToggle(id)}
      >
        <CardTitle className="flex items-center gap-2 text-base">
          <Icon className="h-4 w-4" />
          {title}
          <Badge variant="outline" className="ml-auto">
            {isExpanded ? 'Collapse' : 'Expand'}
          </Badge>
        </CardTitle>
      </CardHeader>
      {isExpanded && (
        <CardContent>
          {children}
        </CardContent>
      )}
    </Card>
  );
}

interface ProofData {
  proofId?: string;
  etid?: number;
  payloadHash?: string;
  timestamp?: string;
  anchors?: Array<{
    id: string;
    type: string;
    value: string;
    timestamp: string;
  }>;
  signatures?: Array<{
    id: string;
    signer: string;
    signature: string;
    timestamp: string;
  }>;
  raw?: any;
}

interface ProofViewerProps {
  readonly proofJson: ProofData;
  readonly isOpen: boolean;
  readonly onClose: () => void;
  readonly triggerRef?: React.RefObject<HTMLElement>;
}

export default function ProofViewer({ proofJson, isOpen, onClose, triggerRef }: ProofViewerProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [copiedFields, setCopiedFields] = useState<Set<string>>(new Set());
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']));
  const dialogRef = useRef<HTMLDivElement>(null);
  const firstFocusableRef = useRef<HTMLButtonElement>(null);

  // Handle keyboard navigation and ESC key
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      // Focus first focusable element when modal opens
      setTimeout(() => {
        firstFocusableRef.current?.focus();
      }, 100);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  // Handle focus trap
  useEffect(() => {
    if (!isOpen) return;

    const handleTabKey = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') return;

      const focusableElements = dialogRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      if (!focusableElements || focusableElements.length === 0) return;

      const firstElement = focusableElements[0] as HTMLElement;
      const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      } else if (document.activeElement === lastElement) {
        event.preventDefault();
        firstElement.focus();
      }
    };

    document.addEventListener('keydown', handleTabKey);
    return () => document.removeEventListener('keydown', handleTabKey);
  }, [isOpen]);

  // Handle modal close and focus return
  const handleClose = () => {
    onClose();
    // Return focus to trigger element
    setTimeout(() => {
      triggerRef?.current?.focus();
    }, 100);
  };

  const copyToClipboard = async (text: string, fieldName: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedFields(prev => new Set([...prev, fieldName]));
      toast.success(`${fieldName} copied to clipboard`);
      
      // Reset copied state after 2 seconds
      setTimeout(() => {
        setCopiedFields(prev => {
          const newSet = new Set(prev);
          newSet.delete(fieldName);
          return newSet;
        });
      }, 2000);
    } catch (error) {
      console.error('Copy to clipboard failed:', error);
      toast.error('Failed to copy to clipboard');
    }
  };

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch (error) {
      console.warn('Failed to parse timestamp:', error);
      return timestamp;
    }
  };

  const formatHash = (hash: string) => {
    if (!hash) return 'N/A';
    return `${hash.substring(0, 8)}...${hash.substring(hash.length - 8)}`;
  };


  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent 
        ref={dialogRef}
        className="max-w-4xl max-h-[90vh] overflow-hidden"
        aria-describedby="proof-description"
      >
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Document Proof Viewer
          </DialogTitle>
          <DialogDescription id="proof-description">
            View detailed proof information for the sealed document
          </DialogDescription>
        </DialogHeader>

        <div className="overflow-y-auto max-h-[calc(90vh-8rem)]">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview" className="flex items-center gap-2">
                <Eye className="h-4 w-4" />
                Overview
              </TabsTrigger>
              <TabsTrigger value="anchors" className="flex items-center gap-2">
                <Anchor className="h-4 w-4" />
                Anchors
              </TabsTrigger>
              <TabsTrigger value="signatures" className="flex items-center gap-2">
                <FileSignature className="h-4 w-4" />
                Signatures
              </TabsTrigger>
              <TabsTrigger value="raw" className="flex items-center gap-2">
                <Code className="h-4 w-4" />
                Raw
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-4">
              <div className="space-y-4">
                <CollapsibleSection 
                  id="overview" 
                  title="Proof Overview" 
                  icon={Shield}
                  defaultExpanded={true}
                  expandedSections={expandedSections}
                  onToggle={toggleSection}
                >
                  <div className="grid gap-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Hash className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium">Payload Hash:</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <code className="text-sm bg-muted px-2 py-1 rounded">
                          {formatHash(proofJson.payloadHash || '')}
                        </code>
                        <CopyButton 
                          text={proofJson.payloadHash || ''} 
                          fieldName="payloadHash" 
                          label="Hash"
                          copiedFields={copiedFields}
                          onCopy={copyToClipboard}
                        />
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Key className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium">Entity Type ID:</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary">
                          {proofJson.etid || 'N/A'}
                        </Badge>
                        <CopyButton 
                          text={String(proofJson.etid || '')} 
                          fieldName="etid" 
                          label="ETID"
                          copiedFields={copiedFields}
                          onCopy={copyToClipboard}
                        />
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Shield className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium">Proof ID:</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <code className="text-sm bg-muted px-2 py-1 rounded">
                          {formatHash(proofJson.proofId || '')}
                        </code>
                        <CopyButton 
                          text={proofJson.proofId || ''} 
                          fieldName="proofId" 
                          label="Proof ID"
                          copiedFields={copiedFields}
                          onCopy={copyToClipboard}
                        />
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium">Timestamp:</span>
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {formatTimestamp(proofJson.timestamp || '')}
                      </span>
                    </div>
                  </div>
                </CollapsibleSection>

                <CollapsibleSection 
                  id="summary" 
                  title="Proof Summary" 
                  icon={FileSignature}
                  expandedSections={expandedSections}
                  onToggle={toggleSection}
                >
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-muted/50 rounded-lg">
                      <div className="text-2xl font-bold text-primary">
                        {proofJson.anchors?.length || 0}
                      </div>
                      <div className="text-sm text-muted-foreground">Anchors</div>
                    </div>
                    <div className="text-center p-4 bg-muted/50 rounded-lg">
                      <div className="text-2xl font-bold text-primary">
                        {proofJson.signatures?.length || 0}
                      </div>
                      <div className="text-sm text-muted-foreground">Signatures</div>
                    </div>
                    <div className="text-center p-4 bg-muted/50 rounded-lg">
                      <div className="text-2xl font-bold text-primary">
                        {proofJson.etid ? 'Sealed' : 'Unknown'}
                      </div>
                      <div className="text-sm text-muted-foreground">Status</div>
                    </div>
                  </div>
                </CollapsibleSection>
              </div>
            </TabsContent>

            <TabsContent value="anchors" className="mt-4">
              <div className="space-y-4">
                <CollapsibleSection 
                  id="anchors" 
                  title="Blockchain Anchors" 
                  icon={Anchor}
                  defaultExpanded={true}
                  expandedSections={expandedSections}
                  onToggle={toggleSection}
                >
                  {proofJson.anchors && proofJson.anchors.length > 0 ? (
                    <div className="space-y-3">
                      {proofJson.anchors.map((anchor, index) => (
                        <Card key={anchor.id || index} className="p-4">
                          <div className="grid gap-2">
                            <div className="flex items-center justify-between">
                              <span className="font-medium">Anchor {index + 1}</span>
                              <Badge variant="outline">{anchor.type}</Badge>
                            </div>
                            <div className="text-sm text-muted-foreground">
                              <strong>ID:</strong> {anchor.id}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              <strong>Value:</strong> 
                              <code className="ml-2 bg-muted px-2 py-1 rounded text-xs">
                                {anchor.value}
                              </code>
                            </div>
                            <div className="text-sm text-muted-foreground">
                              <strong>Timestamp:</strong> {formatTimestamp(anchor.timestamp)}
                            </div>
                          </div>
                        </Card>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <Anchor className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No anchors found in this proof</p>
                    </div>
                  )}
                </CollapsibleSection>
              </div>
            </TabsContent>

            <TabsContent value="signatures" className="mt-4">
              <div className="space-y-4">
                <CollapsibleSection 
                  id="signatures" 
                  title="Digital Signatures" 
                  icon={FileSignature}
                  defaultExpanded={true}
                  expandedSections={expandedSections}
                  onToggle={toggleSection}
                >
                  {proofJson.signatures && proofJson.signatures.length > 0 ? (
                    <div className="space-y-3">
                      {proofJson.signatures.map((signature, index) => (
                        <Card key={signature.id || index} className="p-4">
                          <div className="grid gap-2">
                            <div className="flex items-center justify-between">
                              <span className="font-medium">Signature {index + 1}</span>
                              <Badge variant="secondary">{signature.signer}</Badge>
                            </div>
                            <div className="text-sm text-muted-foreground">
                              <strong>ID:</strong> {signature.id}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              <strong>Signature:</strong>
                              <code className="ml-2 bg-muted px-2 py-1 rounded text-xs block mt-1 break-all">
                                {signature.signature}
                              </code>
                            </div>
                            <div className="text-sm text-muted-foreground">
                              <strong>Timestamp:</strong> {formatTimestamp(signature.timestamp)}
                            </div>
                          </div>
                        </Card>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <FileSignature className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No signatures found in this proof</p>
                    </div>
                  )}
                </CollapsibleSection>
              </div>
            </TabsContent>

            <TabsContent value="raw" className="mt-4">
              <div className="space-y-4">
                <CollapsibleSection 
                  id="raw" 
                  title="Raw Proof Data" 
                  icon={Code}
                  defaultExpanded={true}
                  expandedSections={expandedSections}
                  onToggle={toggleSection}
                >
                  <div className="bg-muted p-4 rounded-lg">
                    <pre className="text-sm overflow-x-auto whitespace-pre-wrap">
                      {JSON.stringify(proofJson.raw || proofJson, null, 2)}
                    </pre>
                  </div>
                  <div className="flex justify-end mt-4">
                    <CopyButton 
                      text={JSON.stringify(proofJson.raw || proofJson, null, 2)} 
                      fieldName="rawData" 
                      label="Raw Data"
                      copiedFields={copiedFields}
                      onCopy={copyToClipboard}
                    />
                  </div>
                </CollapsibleSection>
              </div>
            </TabsContent>
          </Tabs>
        </div>

        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button 
            ref={firstFocusableRef}
            variant="outline" 
            onClick={handleClose}
          >
            Close
          </Button>
          <Button asChild>
            <a 
              href={`/api/proof?id=${proofJson.proofId || proofJson.etid}`} 
              target="_blank" 
              rel="noopener noreferrer"
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Download Proof
            </a>
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
