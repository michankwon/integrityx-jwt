export default function BaseFooter() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 bg-muted">
      <div className="container grid items-center justify-center gap-4 px-4 text-center md:px-6">
        <div className="space-y-3">
          <h2 className="text-3xl font-semibold tracking-tighter md:text-4xl/tight">Manage Your Blog with Ease</h2>
          <p className="mx-auto max-w-[600px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">Our powerful CMS allows you to effortlessly create, edit, and publish your blog content.</p>
        </div>
      </div>
    </section>
  );
}
