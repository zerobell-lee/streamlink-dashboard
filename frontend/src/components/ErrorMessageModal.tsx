'use client';

import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { X, AlertCircle, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import clsx from 'clsx';

interface ErrorMessageModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  errorMessage: string;
  recordingInfo?: {
    fileName: string;
    streamerName: string;
    platform: string;
    startTime: string;
  };
}

export default function ErrorMessageModal({
  isOpen,
  onClose,
  title,
  errorMessage,
  recordingInfo
}: ErrorMessageModalProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      let copyText = errorMessage;
      if (recordingInfo) {
        copyText = `Recording: ${recordingInfo.fileName}
Streamer: ${recordingInfo.streamerName}
Platform: ${recordingInfo.platform}
Start Time: ${recordingInfo.startTime}

Error Message:
${errorMessage}`;
      }

      await navigator.clipboard.writeText(copyText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  const formatErrorMessage = (message: string) => {
    // Split by common section headers and format them
    const sections = message.split(/(?=--- \w+)/);
    return sections.map((section, index) => {
      const lines = section.trim().split('\n');
      const firstLine = lines[0];

      // Check if it's a section header
      if (firstLine.match(/^--- .+ ---$/)) {
        return (
          <div key={index} className="mt-4 first:mt-0">
            <div className="font-semibold text-gray-900 bg-gray-100 px-3 py-2 rounded-t border-l-4 border-red-500">
              {firstLine.replace(/^--- (.+) ---$/, '$1')}
            </div>
            <div className="bg-gray-50 px-3 py-2 rounded-b border border-gray-200 border-t-0">
              <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                {lines.slice(1).join('\n').trim()}
              </pre>
            </div>
          </div>
        );
      } else {
        return (
          <div key={index} className="mt-2 first:mt-0">
            <pre className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-3 rounded border">
              {section}
            </pre>
          </div>
        );
      }
    });
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-10" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-4xl transform overflow-hidden rounded-lg bg-white p-6 text-left align-middle shadow-xl transition-all">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <AlertCircle className="h-6 w-6 text-red-600" />
                    </div>
                    <div>
                      <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-gray-900">
                        {title}
                      </Dialog.Title>
                      {recordingInfo && (
                        <div className="mt-1 text-sm text-gray-600 space-y-1">
                          <div><span className="font-medium">File:</span> {recordingInfo.fileName}</div>
                          <div><span className="font-medium">Streamer:</span> {recordingInfo.streamerName}</div>
                          <div><span className="font-medium">Platform:</span> {recordingInfo.platform}</div>
                          <div><span className="font-medium">Start Time:</span> {recordingInfo.startTime}</div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={handleCopy}
                      className={clsx(
                        "flex items-center space-x-1 px-3 py-1.5 text-sm rounded-md border transition-colors",
                        copied
                          ? "bg-green-50 border-green-200 text-green-700"
                          : "bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100"
                      )}
                    >
                      {copied ? (
                        <>
                          <Check className="h-4 w-4" />
                          <span>Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="h-4 w-4" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>

                    <button
                      type="button"
                      className="text-gray-400 hover:text-gray-600 transition-colors"
                      onClick={onClose}
                    >
                      <span className="sr-only">Close</span>
                      <X className="h-6 w-6" />
                    </button>
                  </div>
                </div>

                <div className="mt-4 max-h-96 overflow-y-auto">
                  {formatErrorMessage(errorMessage)}
                </div>

                <div className="mt-6 flex justify-end">
                  <button
                    type="button"
                    className="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    onClick={onClose}
                  >
                    Close
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}