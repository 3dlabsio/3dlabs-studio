#ifndef slic3r_ION_hpp_
#define slic3r_ION_hpp_

#include <string>
#include <wx/string.h>
#include <boost/optional.hpp>

#include "PrintHost.hpp"

namespace Slic3r {

class DynamicPrintConfig;
class Http;

class ION : public PrintHost
{
public:
    ION(DynamicPrintConfig *config);
    ~ION() override = default;

    const char* get_name() const override;

    bool test(wxString &curl_msg) const override;
    wxString get_test_ok_msg () const override;
    wxString get_test_failed_msg (wxString &msg) const override;
    bool upload(PrintHostUpload upload_data, ProgressFn prorgess_fn, ErrorFn error_fn) const override;
    bool has_auto_discovery() const override { return false; }
    bool can_test() const override { return true; }
    PrintHostPostUploadActions get_post_upload_actions() const override { return PrintHostPostUploadAction::StartPrint; }
    bool supports_multiple_printers() const override { return true; }
    std::string get_host() const override { return host; }
    
    bool get_groups(wxArrayString &groups) const override;
    bool get_printers(wxArrayString &printers) const override;

protected:
    virtual bool validate_version_text(const boost::optional<std::string> &version_text) const;

private:
    std::string host;
    std::string apikey;
    std::string cafile;
    std::string port;

    void set_auth(Http &http) const;
    std::string make_url(const std::string &path) const;
};

}

#endif
