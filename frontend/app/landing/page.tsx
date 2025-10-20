import Link from 'next/link'
import { Shield, FileText, TrendingUp, Lock, Zap, Users } from 'lucide-react'

export default function LandingPage() {
  const features = [
    {
      icon: FileText,
      title: 'Document Verification',
      description: 'Upload and verify document integrity with blockchain-backed security'
    },
    {
      icon: Shield,
      title: 'Attestations',
      description: 'Create and manage document attestations with cryptographic proof'
    },
    {
      icon: Lock,
      title: 'Provenance Tracking',
      description: 'Track complete document lineage and relationships'
    },
    {
      icon: TrendingUp,
      title: 'Predictive Analytics',
      description: 'AI-powered risk prediction and compliance forecasting'
    },
    {
      icon: Zap,
      title: 'Voice Commands',
      description: 'Control operations with natural voice commands'
    },
    {
      icon: Users,
      title: 'Multi-Party Verification',
      description: 'Privacy-preserving third-party document authentication'
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Walacor Financial
            <span className="block text-blue-600">Integrity Platform</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Secure document verification, attestations, and compliance management 
            for financial institutions
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link 
              href="/sign-in"
              className="px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
            >
              Sign In
            </Link>
            <Link 
              href="/sign-up"
              className="px-8 py-4 bg-white text-blue-600 font-semibold border-2 border-blue-600 rounded-lg hover:bg-blue-50 transition-colors shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
            >
              Get Started
            </Link>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Key Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <div 
                key={index}
                className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-200 border border-gray-100"
              >
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <Icon className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            )
          })}
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white/50 backdrop-blur-sm py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <p className="text-4xl font-bold text-blue-600 mb-2">99.9%</p>
              <p className="text-gray-600">System Uptime</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-blue-600 mb-2">256-bit</p>
              <p className="text-gray-600">Encryption</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-blue-600 mb-2">24/7</p>
              <p className="text-gray-600">Support</p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-12 text-center shadow-2xl">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-blue-100 mb-8 max-w-2xl mx-auto">
            Join financial institutions worldwide in securing their document integrity
          </p>
          <Link 
            href="/sign-up"
            className="inline-block px-8 py-4 bg-white text-blue-600 font-semibold rounded-lg hover:bg-gray-100 transition-colors shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
          >
            Create Free Account
          </Link>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            © 2025 Walacor Financial Integrity Platform. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  )
}
