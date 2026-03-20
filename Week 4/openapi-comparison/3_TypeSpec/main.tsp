import "@typespec/http";

using TypeSpec.Http;

@service({
  title: "Library API",
})
namespace LibraryService;

model Book {
  @key id: string;
  title: string;
  author: string;
}

@route("/books")
interface Books {
  @get list(): Book[];

  @post add(@body book: Book): { @statusCode _: 201 };

  @route("/{id}")
  @put update(@path id: string, @body book: Book): Book;

  @route("/{id}")
  @delete remove(@path id: string): { @statusCode _: 204 };
}
