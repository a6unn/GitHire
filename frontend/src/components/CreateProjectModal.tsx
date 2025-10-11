import { Fragment, useState } from 'react';
import { Dialog, Transition, Tab } from '@headlessui/react';
import { XMarkIcon, SparklesIcon, Cog6ToothIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { projectsApi } from '../api/projects';
import type { CreateProjectRequest, QuickStartParseResponse } from '../types/project';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { FormError } from './FormError';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
}

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

export default function CreateProjectModal({ isOpen, onClose }: CreateProjectModalProps) {
  // Common state
  const [formData, setFormData] = useState<CreateProjectRequest>({
    name: '',
    job_title: '',
    job_description_text: '',
    location: '',
  });
  const [errors, setErrors] = useState<Partial<Record<keyof CreateProjectRequest, string>>>({});

  // Quick Start state
  const [quickText, setQuickText] = useState('');
  const [parsedData, setParsedData] = useState<QuickStartParseResponse | null>(null);
  const [isParsing, setIsParsing] = useState(false);
  const [parseError, setParseError] = useState<string>('');

  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const createMutation = useMutation({
    mutationFn: projectsApi.createProject,
    onSuccess: (project) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      onClose();
      resetAllForms();
      navigate(`/projects/${project.project_id}`);
    },
    onError: (error: any) => {
      console.error('Failed to create project:', error);
      setErrors({
        name: error.response?.data?.detail || 'Failed to create project. Please try again.',
      });
    },
  });

  const resetAllForms = () => {
    setFormData({ name: '', job_title: '', job_description_text: '', location: '' });
    setErrors({});
    setQuickText('');
    setParsedData(null);
    setParseError('');
  };

  const handleParseQuickStart = async () => {
    if (!quickText.trim() || quickText.trim().length < 10) {
      setParseError('Please describe what you\'re looking for (at least 10 characters)');
      return;
    }

    setIsParsing(true);
    setParseError('');

    try {
      const parsed = await projectsApi.parseQuickStart(quickText);
      setParsedData(parsed);

      // Auto-fill form data with parsed values
      setFormData({
        name: parsed.project_name,
        job_title: parsed.job_title,
        job_description_text: parsed.job_description_text,
        location: parsed.location || '',
      });
    } catch (error: any) {
      console.error('Failed to parse quick start:', error);
      setParseError(error.response?.data?.detail || 'Failed to parse. Please try again or use Advanced mode.');
    } finally {
      setIsParsing(false);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof CreateProjectRequest, string>> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Project name is required';
    } else if (formData.name.length > 255) {
      newErrors.name = 'Project name must be less than 255 characters';
    }

    if (!formData.job_title.trim()) {
      newErrors.job_title = 'Job title is required';
    } else if (formData.job_title.length > 255) {
      newErrors.job_title = 'Job title must be less than 255 characters';
    }

    if (!formData.job_description_text.trim()) {
      newErrors.job_description_text = 'Job description is required';
    } else if (formData.job_description_text.length < 10) {
      newErrors.job_description_text = 'Job description must be at least 10 characters';
    } else if (formData.job_description_text.length > 10000) {
      newErrors.job_description_text = 'Job description must be less than 10000 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }
    if (validateForm()) {
      createMutation.mutate(formData);
    }
  };

  const handleClose = () => {
    if (!createMutation.isPending && !isParsing) {
      onClose();
      resetAllForms();
    }
  };

  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={handleClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6">
                <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                  <button
                    type="button"
                    className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    onClick={handleClose}
                    disabled={createMutation.isPending || isParsing}
                  >
                    <span className="sr-only">Close</span>
                    <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                  </button>
                </div>

                <div className="sm:flex sm:items-start">
                  <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                    <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                      Create New Project
                    </Dialog.Title>
                    <div className="mt-2">
                      <p className="text-sm text-gray-500">
                        Create a new recruitment project to start sourcing and ranking candidates.
                      </p>
                    </div>

                    {/* Tabbed Interface */}
                    <Tab.Group as="div" className="mt-6">
                      <Tab.List className="flex space-x-1 rounded-xl bg-blue-50 p-1">
                        <Tab
                          className={({ selected }) =>
                            classNames(
                              'w-full rounded-lg py-2.5 text-sm font-medium leading-5 transition-all',
                              'ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2',
                              selected
                                ? 'bg-white text-blue-700 shadow'
                                : 'text-blue-600 hover:bg-white/[0.4] hover:text-blue-700'
                            )
                          }
                        >
                          <div className="flex items-center justify-center gap-2">
                            <SparklesIcon className="h-5 w-5" />
                            <span>Quick Start</span>
                          </div>
                        </Tab>
                        <Tab
                          className={({ selected }) =>
                            classNames(
                              'w-full rounded-lg py-2.5 text-sm font-medium leading-5 transition-all',
                              'ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2',
                              selected
                                ? 'bg-white text-blue-700 shadow'
                                : 'text-blue-600 hover:bg-white/[0.4] hover:text-blue-700'
                            )
                          }
                        >
                          <div className="flex items-center justify-center gap-2">
                            <Cog6ToothIcon className="h-5 w-5" />
                            <span>Advanced</span>
                          </div>
                        </Tab>
                      </Tab.List>

                      <Tab.Panels className="mt-6">
                        {/* Quick Start Panel */}
                        <Tab.Panel className="space-y-6">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Describe what you're looking for:
                            </label>
                            <textarea
                              rows={4}
                              value={quickText}
                              onChange={(e) => setQuickText(e.target.value)}
                              placeholder="e.g., Senior Python developers in Chennai with Django and FastAPI experience for our Q1 2025 hiring"
                              disabled={isParsing || createMutation.isPending}
                              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
                            />
                            <p className="mt-1 text-xs text-gray-500">
                              Use natural language - mention role, location, skills, and any other details
                            </p>
                            {parseError && <FormError message={parseError} />}
                          </div>

                          {!parsedData ? (
                            <Button
                              type="button"
                              variant="primary"
                              onClick={handleParseQuickStart}
                              isLoading={isParsing}
                              disabled={isParsing || !quickText.trim() || quickText.trim().length < 10}
                              className="w-full"
                            >
                              {isParsing ? 'Analyzing...' : 'Analyze & Extract Details'}
                            </Button>
                          ) : (
                            <div className="space-y-4">
                              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                                <h4 className="text-sm font-semibold text-green-900 mb-3 flex items-center gap-2">
                                  <CheckCircleIcon className="h-5 w-5 text-green-600" />
                                  Auto-detected fields:
                                </h4>
                                <div className="space-y-2">
                                  <div className="flex items-start gap-2">
                                    <span className="text-xs font-medium text-green-700 min-w-[120px]">Project Name:</span>
                                    <Input
                                      type="text"
                                      value={formData.name}
                                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                      className="flex-1 text-sm"
                                    />
                                  </div>
                                  <div className="flex items-start gap-2">
                                    <span className="text-xs font-medium text-green-700 min-w-[120px]">Job Title:</span>
                                    <Input
                                      type="text"
                                      value={formData.job_title}
                                      onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
                                      className="flex-1 text-sm"
                                    />
                                  </div>
                                  <div className="flex items-start gap-2">
                                    <span className="text-xs font-medium text-green-700 min-w-[120px]">Location:</span>
                                    <Input
                                      type="text"
                                      value={formData.location}
                                      onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                                      placeholder="Optional"
                                      className="flex-1 text-sm"
                                    />
                                  </div>
                                  {parsedData.skills.length > 0 && (
                                    <div className="flex items-start gap-2">
                                      <span className="text-xs font-medium text-green-700 min-w-[120px]">Skills:</span>
                                      <div className="flex-1 flex flex-wrap gap-1">
                                        {parsedData.skills.map((skill, i) => (
                                          <span key={i} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                            {skill}
                                          </span>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                  {parsedData.experience_years && (
                                    <div className="flex items-start gap-2">
                                      <span className="text-xs font-medium text-green-700 min-w-[120px]">Experience:</span>
                                      <span className="text-sm text-green-900">{parsedData.experience_years}</span>
                                    </div>
                                  )}
                                </div>
                              </div>

                              <div className="flex gap-3">
                                <Button
                                  type="button"
                                  variant="secondary"
                                  onClick={() => {
                                    setParsedData(null);
                                    setQuickText('');
                                    setFormData({ name: '', job_title: '', job_description_text: '', location: '' });
                                  }}
                                  className="flex-1"
                                >
                                  Start Over
                                </Button>
                                <Button
                                  type="button"
                                  variant="primary"
                                  onClick={handleSubmit}
                                  isLoading={createMutation.isPending}
                                  disabled={createMutation.isPending}
                                  className="flex-1"
                                >
                                  Create Project
                                </Button>
                              </div>
                            </div>
                          )}
                        </Tab.Panel>

                        {/* Advanced Panel */}
                        <Tab.Panel>
                          <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                                Project Name *
                              </label>
                              <Input
                                id="name"
                                type="text"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                placeholder="e.g., Q1 2025 Python Hiring"
                                disabled={createMutation.isPending}
                                className="mt-1"
                              />
                              {errors.name && <FormError message={errors.name} />}
                            </div>

                            <div>
                              <label htmlFor="job_title" className="block text-sm font-medium text-gray-700">
                                Job Title *
                              </label>
                              <Input
                                id="job_title"
                                type="text"
                                value={formData.job_title}
                                onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
                                placeholder="e.g., Senior Python Developer"
                                disabled={createMutation.isPending}
                                className="mt-1"
                              />
                              {errors.job_title && <FormError message={errors.job_title} />}
                            </div>

                            <div>
                              <label htmlFor="location" className="block text-sm font-medium text-gray-700">
                                Location
                              </label>
                              <Input
                                id="location"
                                type="text"
                                value={formData.location}
                                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                                placeholder="e.g., Chennai, Tamil Nadu, India"
                                disabled={createMutation.isPending}
                                className="mt-1"
                              />
                              <p className="mt-1 text-xs text-gray-500">
                                Optional. Leave blank for remote/global search.
                              </p>
                              {errors.location && <FormError message={errors.location} />}
                            </div>

                            <div>
                              <label htmlFor="job_description_text" className="block text-sm font-medium text-gray-700">
                                Job Description *
                              </label>
                              <textarea
                                id="job_description_text"
                                rows={6}
                                value={formData.job_description_text}
                                onChange={(e) => setFormData({ ...formData, job_description_text: e.target.value })}
                                placeholder="Paste the full job description here..."
                                disabled={createMutation.isPending}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
                              />
                              {errors.job_description_text && <FormError message={errors.job_description_text} />}
                            </div>

                            <div className="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                              <Button
                                type="submit"
                                variant="primary"
                                isLoading={createMutation.isPending}
                                disabled={createMutation.isPending}
                                className="sm:col-start-2"
                              >
                                Create Project
                              </Button>
                              <Button
                                type="button"
                                variant="secondary"
                                onClick={handleClose}
                                disabled={createMutation.isPending}
                                className="mt-3 sm:col-start-1 sm:mt-0"
                              >
                                Cancel
                              </Button>
                            </div>
                          </form>
                        </Tab.Panel>
                      </Tab.Panels>
                    </Tab.Group>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
}
