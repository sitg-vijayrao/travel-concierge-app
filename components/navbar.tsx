import { SignedIn, UserButton } from "@clerk/nextjs";
export const Navbar = () => {
  return (
    <div className="p-2 flex flex-row gap-2 justify-between">
      <SignedIn>
        <UserButton />
      </SignedIn>
    </div>
  );
};
