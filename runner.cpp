#include <aws/lambda-runtime/runtime.h>
#include <iostream>

using namespace std;
using namespace aws::lambda_runtime;

invocation_response my_handler(invocation_request const& request)
{
   return invocation_response::success("Walkk suceeded.", "application/json");
}

int main() {
            
              run_handler(my_handler);
              
              return 0;
}
