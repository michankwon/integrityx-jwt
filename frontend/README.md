# Walacor Template

This template is designed to embellish the process of integrating with the Walacor data platform.

## About Walacor

An Enterprise level secure data platform with a database look and feel while integrating industry best practices, including blockchain, to provide a quantum resistant tamper-proof data repository.

### Introduction

The primary design goal of the document is to assist users with their knowledge of the Platform application.

However, there is a lot going on under the hood and it is important to gain some knowledge to make best use of The Platform.

### Immutability

Because the platform integrates blockchain, an important difference that one must be aware of is immutability. EVERYTHING (Data, Schema, Users, etc.) submitted to the platform is part of a never changing audit log that can never be deleted.

The Platform handles the heavy lifting of this for the user and, in general, allows the user to interact with it as one does with most databases. However, it is best to keep this in mind when doing things like Schema design.

[Official Walacor Documentation](https://admindoc.walacor.com/admin-documentation/latest/the-platform-application-an-introduction)

# Important

To make this work, you will need to add an .env file with these variables. Here is a video tutorial explaining these.

```bash
# From Walacor
NEXT_PUBLIC_EC2_WALACOR="YOUR_EC2"
NEXT_PUBLIC_WALACOR_BLOG_ETID="YOUR_BLOG_ETID"
NEXT_PUBLIC_WALACOR_USERNAME="YOUR_USERNAME"
NEXT_PUBLIC_WALACOR_PASSWORD="YOUR_PASSWORD"

# From AWS
NEXT_PUBLIC_AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"
NEXT_PUBLIC_AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY"
NEXT_PUBLIC_AWS_REGION="YOUR_AWS_REGION"
NEXT_PUBLIC_AWS_S3_BUCKET="YOUR_S3_BUCKET"

# From Clerk
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="YOUR_CLERK_PUBLISHABLE_KEY"
CLERK_SECRET_KEY="YOUR_CLERK_SECRET_KEY"
NEXT_PUBLIC_CLERK_SIGN_IN_URL="/sign-in"
NEXT_PUBLIC_CLERK_SIGN_UP_URL="/sign-up"
```

## Getting Started

To create a new Walacor project, use the following command:

```bash
npx create-walacor-app <project-name>
```

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/basic-features/font-optimization) to automatically optimize and load Inter, a custom Google Font.
